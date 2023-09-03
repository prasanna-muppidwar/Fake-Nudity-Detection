import os
from tabnanny import filename_only
import requests
from flask import Flask, request, render_template
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
        method = request.form['language']
        if method == 'url-search':
            image_url = request.form['text']
            is_nsfw, nsfw_score, image_path = detect_nsfw_image_url(image_url)
            return render_template('results.html', is_nsfw=is_nsfw, nsfw_score=nsfw_score, image_path=image_path)

        elif method == 'upload-search':
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

                is_nsfw, nsfw_score, image_path = detect_nsfw_image_file(filepath)
                return render_template('results.html', is_nsfw=is_nsfw, nsfw_score=nsfw_score, image_path=image_path)

        elif method == 'key-search':
            original_text = request.form['text']
            target_language = request.form['target_language']  # Replace with your translation logic
            return render_template('results.html', original_text=original_text, target_language=target_language)

    return render_template('index.html')

def detect_nsfw_image_file(filepath):
    # Call the DeepAI NSFW Detector API to scan the uploaded image
    api_url = "https://api.deepai.org/api/nsfw-detector"
    headers = {
        'api-key': DEEPAI_API_KEY,
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
                image_path = None  # Initialize image_path as None

                # If the image is NSFW, provide the image path to display in the template
                if is_nsfw:
                    image_path = '/static/uploads/' + filename_only  # Change the path as needed

                return is_nsfw, nsfw_score, image_path
            else:
                return False, None, None

    except Exception as e:
        print(str(e))
        return False, None, None

def detect_nsfw_image_url(image_url):
    # Call the DeepAI NSFW Detector API to scan the image URL
    api_url = "https://api.deepai.org/api/nsfw-detector"
    headers = {
        'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K',
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
            image_path = None  # Initialize image_path as None

            # If the image is NSFW, provide the image path to display in the template
            if is_nsfw:
                image_path = image_url  # You can provide the URL itself as the image path

            return is_nsfw, nsfw_score, image_path
        else:
            return False, None, image_url

    except Exception as e:
        print(str(e))
        return False, None, image_url

if __name__ == '__main__':
    app.run(debug=True)
