
from distutils.util import strtobool
import json
import os
import io

# Imports for the REST API
from flask import Flask, request, jsonify

# Imports for image procesing
from PIL import Image

# Imports for prediction
from predict import initialize, predict_image, predict_url

app = Flask(__name__)
app_port = os.getenv('IMAGE_CLASSIFIER_PORT', '8580')

# 4MB Max image size limit
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 

# Default route just shows simple text
@app.route('/')
def index():
    return 'CustomVision.ai model host harness'

# Like the CustomVision.ai Prediction service /image route handles either
#     - octet-stream image file 
#     - a multipart/form-data with files in the imageData parameter
@app.route('/image', methods=['POST'])
@app.route('/custom-vision-edge/image', methods=['POST'])
@app.route('/custom-vision-edge/image/nostore', methods=['POST'])
@app.route('/custom-vision-edge/classify/iterations/demo-pi/image', methods=['POST'])
@app.route('/custom-vision-edge/classify/iterations/demo-pi/image/nostore', methods=['POST'])
@app.route('/custom-vision-edge/detect/iterations/demo-pi/image', methods=['POST'])
@app.route('/custom-vision-edge/detect/iterations/demo-pi/image/nostore', methods=['POST'])
def predict_image_handler(project=None, publishedName=None):
    try:
        imageData = None
        if ('imageData' in request.files):
            imageData = request.files['imageData']
        elif ('imageData' in request.form):
            imageData = request.form['imageData']
        else:
            imageData = io.BytesIO(request.get_data())

        img = Image.open(imageData)
        results = predict_image(img)
        return jsonify(results)
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image', 500


# Like the CustomVision.ai Prediction service /url route handles url's
# in the body of the request of the form:
#     { 'Url': '<http url>'}  
@app.route('/url', methods=['POST'])
@app.route('/custom-vision-edge/url', methods=['POST'])
@app.route('/custom-vision-edge/url/nostore', methods=['POST'])
@app.route('/custom-vision-edge/classify/iterations/demo-pi/url', methods=['POST'])
@app.route('/custom-vision-edge/classify/iterations/demo-pi/url/nostore', methods=['POST'])
@app.route('/custom-vision-edge/detect/iterations/demo-pi/url', methods=['POST'])
@app.route('/custom-vision-edge/detect/iterations/demo-pi/url/nostore', methods=['POST'])
def predict_url_handler(project=None, publishedName=None):
    try:
        image_url = json.loads(request.get_data().decode('utf-8'))['url']
        results = predict_url(image_url)
        return jsonify(results)
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image'
    
def convert_string_to_bool(env):
    try:
        return bool(strtobool(env))
    except ValueError:
        raise ValueError('Could not convert string to bool.')    

if __name__ == '__main__':
    # Load and intialize the model
    initialize()

    # Run the server
    app.run(host='0.0.0.0', port=app_port)

