import json
import uuid
import os
import requests
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, request, render_template, session
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

# Define the directory where uploaded images will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define allowed image file extensions (you can extend this list)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Function to check if a filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def index_post():
    # Check if a file was uploaded
    if 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        
        if file and allowed_file(file.filename):
            # Save the uploaded file to the UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Perform image processing (replace this with your actual image processing logic)
            # Here, we're assuming you're using a hypothetical image processing function
            # called process_image that takes the filepath as input and returns some result.
            image_processing_result = process_image(filepath)
            
            return render_template('results.html', image_processing_result=image_processing_result)
        else:
            return render_template('index.html', error='Invalid file format')

    # If no file was uploaded, continue with text translation as before
    original_text = request.form['text']
    target_language = request.form['language']
    
    # ... (the rest of your translation logic)

    return render_template(
        'results.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language
    )

if __name__ == '__main__':
    app.run(debug=True)
