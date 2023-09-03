import os
import requests
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)


# Define the DeepAI API key from your account (replace 'your-api-key' with your actual key)
DEEPAI_API_KEY = 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'

# Define the directory where uploaded images will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define allowed image file extensions (you can extend this list)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Function to check if a filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the user selected 'Image URL' option
        if request.form['language'] == 'url-search':
            image_url = request.form['text']
            is_nsfw, nsfw_score = detect_nsfw_image_url(image_url)
            return render_template('results.html', is_nsfw=is_nsfw, nsfw_score=nsfw_score)

        # Check if a file was uploaded
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return render_template('index.html', error='No selected file')

            # Check if the file is allowed (image format)
            if not allowed_file(file.filename):
                return render_template('index.html', error='Invalid file format')

            # Save the uploaded file to the UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            is_nsfw, nsfw_score = detect_nsfw_image_file(filepath)
            return render_template('results.html', is_nsfw=is_nsfw, nsfw_score=nsfw_score)

    return render_template('index.html')

def detect_nsfw_image_file(filepath):
    # Call the DeepAI NSFW Detector API to scan the uploaded image
    api_url = "https://api.deepai.org/api/nsfw-detector"
    headers = {
        'api-key':'quickstart-QUdJIGlzIGNvbWluZy4uLi4K',
    }

    try:
        with open(filepath, 'rb') as image_file:
            files = {'image': (os.path.basename(filepath), image_file)}
            response = requests.post(api_url, files=files, headers=headers)
            result = response.json()
            # Extract the NSFW score
            nsfw_score = result.get('output', {}).get('nsfw_score', None)

            if nsfw_score is not None:
                # Determine if the image contains NSFW content based on the threshold
                threshold = 0.5  # Adjust this threshold as needed
                is_nsfw = nsfw_score >= threshold
                return is_nsfw, nsfw_score
            else:
                return False, None

    except Exception as e:
        print(str(e))
        return False, None

def detect_nsfw_image_url(image_url):
    # Call the DeepAI NSFW Detector API to scan the image URL
    api_url = "https://api.deepai.org/api/nsfw-detector"
    headers = {
        'api-key': DEEPAI_API_KEY,
    }

    data = {'image': image_url}

    try:
        response = requests.post(api_url, data=data, headers=headers)
        result = response.json()
        # Extract the NSFW score
        nsfw_score = result.get('output', {}).get('nsfw_score', None)

        if nsfw_score is not None:
            # Determine if the image contains NSFW content based on the threshold
            threshold = 0.5  # Adjust this threshold as needed
            is_nsfw = nsfw_score >= threshold
            return is_nsfw, nsfw_score
        else:
            return False, None

    except Exception as e:
        print(str(e))
        return False, None

if __name__ == '__main__':
    app.run(debug=True)
