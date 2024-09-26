from flask import Flask, request, jsonify
import cv2
import numpy as np
import pytesseract
from ktpocr import KTPOCR
import os

app = Flask(__name__)

# Set the path to the Tesseract executable if needed
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

@app.route('/ocr', methods=['POST'])
def ocr():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Read the image
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'error': 'Unable to read the image'}), 400

    # Use the KTPOCR class for OCR processing
    ocr = KTPOCR(img)
    final_results = ocr.to_json()  # Assuming this method exists in KTPOCR

    return jsonify({'result': final_results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Change to your desired port
