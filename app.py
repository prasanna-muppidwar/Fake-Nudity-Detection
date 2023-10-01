import streamlit as st
import requests
import os
from werkzeug.utils import secure_filename
from decouple import config

DEEPAI_API_KEY = config("DEEPAI_API_KEY")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

st.title("Fake Nude Detection Portal")

selected_method = st.selectbox("Select Method:", ["Search Entirely by Key Word", "Upload URL", "Upload Image"])

if selected_method == "Search Entirely by Key Word":
    keyword = st.text_input("Enter Key Word:")
    if st.button("Generate!"):
        st.write("You selected the 'Search Entirely by Key Word' method.")
        st.write(f"You entered the keyword: {keyword}")

elif selected_method == "Upload URL":
    url = st.text_input("Enter URL:")
    if st.button("Generate!"):
        st.write("You selected the 'Upload URL' method.")
        st.write(f"You entered the URL: {url}")

elif selected_method == "Upload Image":
    uploaded_file = st.file_uploader("Upload Image:", type=["jpg", "jpeg", "png", "gif"])
    if uploaded_file is not None:
        if allowed_file(uploaded_file.name):
            if st.button("Generate!"):
                if not os.path.exists("tmp"):
                    os.makedirs("tmp")

                tmp_path = os.path.join("tmp", uploaded_file.name)
                with open(tmp_path, "wb") as f:
                    f.write(uploaded_file.read())

                st.write("You selected the 'Upload Image' method.")

                api_url = "https://api.deepai.org/api/nsfw-detector"

                headers = {
                    "api-key": DEEPAI_API_KEY,
                }

                try:
                    with open(tmp_path, "rb") as image_file:
                        files = {"image": (os.path.basename(tmp_path), image_file)}
                        response = requests.post(api_url, files=files, headers=headers)
                        result = response.json()

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
