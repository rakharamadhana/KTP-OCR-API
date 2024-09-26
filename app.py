from flask import Flask, request, jsonify
import cv2
import numpy as np
from ktpocr import KTPOCR
import json

app = Flask(__name__)

# Define the maximum file size (in bytes)
MAX_FILE_SIZE = 3 * 1024 * 1024

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check file size
    if file.content_length > MAX_FILE_SIZE:
        return jsonify({'error': f'File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)} MB'}), 400

    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'Unable to read the image'}), 400

    try:
        ocr = KTPOCR(img)  # Create an instance of KTPOCR with the image
        ordered_dict = ocr.result.to_ordered_dict()  # Get the ordered dict
        raw_result = ocr.to_raw_result()  # Get the raw OCR result
        return jsonify({
            'raw': raw_result,  # Return the raw OCR text
            'parsed': ordered_dict  # Return the ordered dict as JSON
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return the error message as JSON

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
