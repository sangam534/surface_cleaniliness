import os
import uuid
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from table_detector import assess_cleanliness

app = Flask(__name__)
# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max limit

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        logger.warning("Upload attempt with no image provided in request")
        return jsonify({"error": "No image provided"}), 400
        
    file = request.files['image']
    
    if file.filename == '':
        logger.warning("Upload attempt with empty filename")
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        # Generate a unique ID to prevent collisions among multiple uploads
        unique_id = str(uuid.uuid4())[:8]
        extension = original_filename.rsplit('.', 1)[1].lower()
        
        filename = f"{unique_id}.{extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Saved uploaded file to {filepath}")
        
        # Get threshold from request or use default
        threshold = request.form.get('threshold', 95.0, type=float)
        
        try:
            # Prepare output path for the processed image
            output_filename = f"{unique_id}_result.jpg"
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Process the image
            result = assess_cleanliness(filepath, output_path=output_filepath, threshold_percent=threshold, show=False)
            
            if result is None:
               logger.error("Assessment returned None")
               return jsonify({"error": "Assessment failed"}), 500
            
            if "error" in result:
                logger.error(f"Assessment error: {result['error']}")
                return jsonify(result), 400
                
            # Ensure the path separator is forward slash for web URLs
            result['result_image_url'] = f"/uploads/{output_filename}"
            
            logger.info("Successfully processed image")
            return jsonify(result), 200
            
        except Exception as e:
            logger.exception("Exception occurred during image processing")
            return jsonify({"error": str(e)}), 500
            
    logger.warning(f"File type not allowed: {file.filename}")
    return jsonify({"error": "File type not allowed"}), 400

# Route to serve the processed and uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=True, host='127.0.0.1', port=5001)
