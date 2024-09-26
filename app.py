from flask import Flask, request, jsonify
import cv2
import numpy as np
from ktpocr import KTPOCR

app = Flask(__name__)


@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'Unable to read the image'}), 400

    ocr = KTPOCR(img)  # Create an instance of KTPOCR with the image
    ordered_dict = ocr.result.to_ordered_dict()  # Get the ordered dict
    response_json = json.dumps(ordered_dict, indent=4)  # Convert to JSON string
    return response_json  # Return the JSON string directly

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
