import streamlit as st
import requests
import os
from werkzeug.utils import secure_filename
from decouple import config

# Read the API key from the .env file
DEEPAI_API_KEY = config("DEEPAI_API_KEY")

# Define allowed file extensions and a function to check them
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Streamlit UI
st.title("Image Classification Portal")

# Create a selection box for choosing the search method
selected_method = st.selectbox("Select Method:", ["Search Entirely by Key Word", "Upload URL", "Upload Image"])

# Create a form based on the selected method
if selected_method == "Search Entirely by Key Word":
    keyword = st.text_input("Enter Key Word:")
    if st.button("Generate!"):
        # Implement keyword-based search logic here
        st.write("You selected the 'Search Entirely by Key Word' method.")
        st.write(f"You entered the keyword: {keyword}")

elif selected_method == "Upload URL":
    url = st.text_input("Enter URL:")
    if st.button("Generate!"):
        # Implement URL-based search logic here
        st.write("You selected the 'Upload URL' method.")
        st.write(f"You entered the URL: {url}")

elif selected_method == "Upload Image":
    uploaded_file = st.file_uploader("Upload Image:", type=["jpg", "jpeg", "png", "gif"])
    if uploaded_file is not None:
        if allowed_file(uploaded_file.name):
            if st.button("Generate!"):
                # Create the 'tmp' directory if it doesn't exist
                if not os.path.exists("tmp"):
                    os.makedirs("tmp")

                # Save the uploaded file to a temporary location
                tmp_path = os.path.join("tmp", uploaded_file.name)
                with open(tmp_path, "wb") as f:
                    f.write(uploaded_file.read())

                # Implement image classification logic using the DeepAI API
                st.write("You selected the 'Upload Image' method.")

                # Define the DeepAI API endpoint for NSFW detection
                api_url = "https://api.deepai.org/api/nsfw-detector"

                # Set headers with the DeepAI API key
                headers = {
                    "api-key": DEEPAI_API_KEY,
                }

                try:
                    # Open the image file and send it to the API for NSFW detection
                    with open(tmp_path, "rb") as image_file:
                        files = {"image": (os.path.basename(tmp_path), image_file)}
                        response = requests.post(api_url, files=files, headers=headers)
                        result = response.json()

                        # Extract classification results from the API response
                        nsfw_classification = result.get("output", {}).get("nsfw_score", "Unknown")

                        st.write(f"NSFW Classification Score: {nsfw_classification}")

                        if isinstance(nsfw_classification, (float, int)) and nsfw_classification >= 0.5:
                            st.write("This image is likely NSFW.")
                        else:
                            st.write("This image is safe.")
                        st.image(tmp_path, caption="Uploaded Image", use_column_width=True)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Invalid file format. Please upload a valid image file (jpg, jpeg, png, gif).")
