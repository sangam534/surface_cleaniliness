import cv2
import numpy as np
import argparse
import sys
import logging
import os

logger = logging.getLogger(__name__)

def get_dominant_color(image, k=3):
    # Convert to HSV to better handle lighting variations
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Focus on the central region to increase the chance of picking the table color
    h, w = hsv_image.shape[:2]
    center_roi = hsv_image[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
    
    # Reshape image to a list of pixels
    pixels = center_roi.reshape((-1, 3))
    # Convert to float32
    pixels = np.float32(pixels)

    # Define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert centers back to 8-bit values
    centers = np.uint8(centers)

    # Find the most frequent label (assuming the table is the largest object in the center)
    label_counts = np.bincount(labels.flatten())
    dominant_label = np.argmax(label_counts)
    dominant_color_hsv = centers[dominant_label]
    return dominant_color_hsv

def detect_table_mask(image, dominant_color_hsv, tolerance=30):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    h_val, s_val, v_val = int(dominant_color_hsv[0]), int(dominant_color_hsv[1]), int(dominant_color_hsv[2])
    
    # Dynamic tolerances based on the saturation and value
    # If the surface is very dark or very bright/white/gray, hue doesn't matter much
    if s_val < 40 or v_val < 40:
        h_tol = 180  # Ignore hue for grays/blacks/whites
        s_tol = max(50, tolerance * 2)
        v_tol = max(60, tolerance * 2)
    else:
        h_tol = min(20, tolerance)
        s_tol = min(60, tolerance * 2)
        v_tol = min(70, tolerance * 2)

    lower_bound = np.array([max(0, h_val - h_tol), max(0, s_val - s_tol), max(0, v_val - v_tol)])
    upper_bound = np.array([min(179, h_val + h_tol), min(255, s_val + s_tol), min(255, v_val + v_tol)])
    
    raw_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    
    # Clean up the mask using morphological operations
    kernel = np.ones((7,7), np.uint8)
    raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find the largest contour in the mask (assuming that's the table)
    contours, _ = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    table_mask = np.zeros_like(raw_mask)
    table_contour = None
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Use convex hull to define the table boundaries smoothly
        # This handles objects that overlap the edges of the table
        hull = cv2.convexHull(largest_contour)
        table_contour = hull
        
        cv2.drawContours(table_mask, [hull], -1, 255, thickness=cv2.FILLED)
        
    return table_mask, raw_mask, table_contour

def detect_anomalies(image, table_mask, raw_mask):
    # 1. Color-based anomalies: things inside the table boundary that don't match table color
    # These are the "holes" in the raw mask that are inside the table mask
    color_anomalies = cv2.bitwise_and(table_mask, cv2.bitwise_not(raw_mask))
    
    # 2. Edge-based anomalies: detecting texture/edges on the table (crumbs, clear spills)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Use Canny edge detection to find sharp boundaries (objects)
    edges = cv2.Canny(blurred, 30, 100)
    
    # Use adaptive thresholding for local contrast changes (stains, spills)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 21, 5)
    
    # Combine edges and adaptive threshold
    edge_anomalies = cv2.bitwise_or(edges, thresh)
    edge_anomalies = cv2.bitwise_and(edge_anomalies, edge_anomalies, mask=table_mask)
    
    # Combine color and edge anomalies
    combined_anomalies = cv2.bitwise_or(color_anomalies, edge_anomalies)
    
    # Morphological operations to group nearby anomaly pixels and remove tiny noise
    kernel = np.ones((5,5), np.uint8)
    anomaly_mask = cv2.morphologyEx(combined_anomalies, cv2.MORPH_OPEN, kernel, iterations=1)
    anomaly_mask = cv2.morphologyEx(anomaly_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    
    # Find contours of the anomalies
    contours, _ = cv2.findContours(anomaly_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out extremely small anomalies (noise) 
    filtered_contours = [c for c in contours if cv2.contourArea(c) > 100]
    
    return filtered_contours, anomaly_mask

def assess_cleanliness(image_path, output_path=None, threshold_percent=95.0, show=False):
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Could not read image at {image_path}")
        return {"error": "Could not read image"}
        
    original = image.copy()
    
    # 1. Find dominant color (assuming it's the table)
    dominant_color_hsv = get_dominant_color(image, k=4)
    
    # 2. Extract table mask
    table_mask, raw_mask, table_contour = detect_table_mask(image, dominant_color_hsv, tolerance=25)
    table_area = cv2.countNonZero(table_mask)
    
    if table_area == 0:
        logger.warning("Could not detect a clear table surface.")
        return {"error": "Could not detect a clear table surface"}
        
    # 3. Detect anomalies (dirt, food, spills) on the table
    anomalies, anomaly_mask = detect_anomalies(image, table_mask, raw_mask)
    
    # 4. Calculate areas
    anomaly_area = 0
    for contour in anomalies:
        anomaly_area += cv2.contourArea(contour)
        
    # Cap anomaly area to table area (in case of overlap issues)
    anomaly_area = min(anomaly_area, table_area)
    
    # 5. Calculate percentage
    clean_area = table_area - anomaly_area
    cleanliness_percentage = (clean_area / table_area) * 100
    
    # 6. Determine status
    if cleanliness_percentage >= threshold_percent:
        status_msg = "Table is clean"
        color = (0, 255, 0) # Green
    else:
        status_msg = "Table is dirty"
        color = (0, 0, 255) # Red
        
    # 7. Visualization
    # Draw table bounding area (using the convex hull)
    if table_contour is not None:
        cv2.drawContours(image, [table_contour], -1, (255, 255, 0), 2)
        
    # Draw anomalies
    for contour in anomalies:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, status_msg, (20, 50), font, 1.5, color, 3)
    cv2.putText(image, f"Cleanliness: {cleanliness_percentage:.1f}%", (20, 100), font, 1, (255, 255, 255), 2)
    
    if show:
        cv2.imshow("Original", original)
        cv2.imshow("Table Mask", table_mask)
        cv2.imshow("Anomalies", anomaly_mask)
        cv2.imshow("Result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    # Save the output
    if output_path is None:
        # Default fallback if not provided
        output_path = image_path.split(".")[0] + "_result.jpg"
        
    cv2.imwrite(output_path, image)
    logger.info(f"Result saved to {output_path}")
    logger.info(f"Status: {status_msg} (Cleanliness: {cleanliness_percentage:.1f}%)")
    
    return {
        "status": status_msg,
        "cleanliness_percentage": round(cleanliness_percentage, 1),
        "output_path": output_path
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Table Cleanliness Detector")
    parser.add_argument("image_path", help="Path to the image to analyze")
    parser.add_argument("--threshold", type=float, default=95.0, help="Cleanliness threshold percentage")
    parser.add_argument("--show", action="store_true", help="Show the image window")
    args = parser.parse_args()
    
    assess_cleanliness(args.image_path, threshold_percent=args.threshold, show=args.show)
