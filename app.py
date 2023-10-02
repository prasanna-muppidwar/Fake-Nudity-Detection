import streamlit as st
import requests
import os
from werkzeug.utils import secure_filename
from decouple import config

# Load environment variables from .env
API_URL = config("API_URL")
API_KEY = config("API_KEY")
API_HOST = config("API_HOST")

# Define the NSFW detection API headers
API_HEADERS = {
    "content-type": "application/json",
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST,
}

# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"jpg", "jpeg", "png", "gif"}

# Streamlit UI
st.title("Fake Nude Detection Portal")
st.write("The Fake Nude Detection System is a machine learning-based project that utilizes advanced image analysis techniques to classify images and generate nudity reports.")

# Create a selection box for choosing the search method
selected_method = st.selectbox("Select Method:", ["Search Entirely by Key Word", "Upload URL", "Upload Image"])

# Initialize payload as an empty dictionary
payload = {}

if selected_method == "Search Entirely by Key Word":
    keyword = st.text_input("Enter Key Word:")
    if st.button("Generate!"):
        # Set the payload for keyword search if needed
        payload = {"keyword": keyword}
        st.write("You selected the 'Search Entirely by Key Word' method.")
        st.write(f"You entered the keyword: {keyword}")

elif selected_method == "Upload URL":
    url = st.text_input("Enter URL:")
    if st.button("Generate!"):
        # Set the payload for URL upload if needed
        payload = {"url": url}
        st.write("You selected the 'Upload URL' method.")
        st.write(f"You entered the URL: {url}")

elif selected_method == "Upload Image":
    uploaded_file = st.file_uploader("Upload Image:", type=["jpg", "jpeg", "png", "gif"])
    if uploaded_file is not None:
        if allowed_file(uploaded_file.name):
            if st.button("Generate!"):
                if not os.path.exists("tmp"):
                    os.makedirs("tmp")

                tmp_path = os.path.join("tmp", secure_filename(uploaded_file.name))
                with open(tmp_path, "wb") as f:
                    f.write(uploaded_file.read())

                st.write("You selected the 'Upload Image' method.")
                # Set the payload for image upload if needed
                payload = {"image_path": tmp_path}

                # Make a request to the NSFW detection API with the appropriate payload
                response = requests.post(API_URL, json=payload, headers=API_HEADERS)

                if response.status_code == 200:
                    result = response.json()
                    nsfw_classification = result.get("output", {})

                    st.write(f"NSFW Classification Score: {nsfw_classification}")

                    # Determine if the image is NSFW based on the classification
                    if nsfw_classification.get("nsfw_score", 0.0) >= 0.5:
                        st.warning("This image is likely NSFW.")
                    else:
                        st.success("This image is safe.")
                    st.image(tmp_path, caption="Uploaded Image", use_column_width=True)
                else:
                    st.error(f"API Request Error: Status Code {response.status_code}")
        else:
            st.warning("Invalid file format. Please upload a valid image file (jpg, jpeg, png, gif).")
