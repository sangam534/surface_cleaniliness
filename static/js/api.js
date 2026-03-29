/**
 * Validates the file and uploads it to the backend for analysis.
 * @param {File} file 
 * @param {string|number} threshold 
 * @returns {Promise<Object>} The analysis result data.
 */
export async function analyzeImage(file, threshold) {
    if (!file.type.match('image.*')) {
        throw new Error('Please upload an image file (PNG, JPG, WEBP)');
    }

    const formData = new FormData();
    formData.append('image', file);
    formData.append('threshold', threshold);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze image');
    }

    return data;
}
