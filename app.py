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

    # Process the image
    final_results = read(img)

    return jsonify({'result': final_results})


def read(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold
    th, threshed = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)

    # Detect
    result = pytesseract.image_to_string(threshed, lang="ind")

    final = []

    # Normalize
    for word in result.split("\n"):
        if "”—" in word:
            word = word.replace("”—", ":")
        if "NIK" in word:
            nik_char = word.split()
        if "?" in word:
            word = word.replace("?", "7")
        final.append(word)

    return final


if __name__ == '__main__':
    app.run(debug=True)