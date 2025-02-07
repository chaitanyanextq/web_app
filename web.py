import streamlit as st
import requests
from docx import Document
from PIL import Image
from github import Github
import pandas as pd
import uuid
import base64

def is_valid_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False
    return False

# Streamlit UI
titlle_left, title_right=st.columns([0.7,0.3])
with titlle_left:
    st.title("NextQ.ai Report Generator")
with title_right:
    logo=Image.open(r"Screenshot 2025-02-04 193738.png")
    st.image(logo,width=300)

st.write("---")

# URL section and URL validation
st.title("Input")
url = st.text_input("Enter URL")
if st.button("Check URL"):
    if is_valid_url(url):
        st.success("The URL is valid!")
    else:
        st.error("The URL is not valid.")

# GitHub credentials
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "chaitanyanextq/web_app"
FILE_PATH = "web_data.csv"  # Path to the CSV in the repository

# Initialize GitHub
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def get_csv_content():
    """Fetch existing CSV from GitHub"""
    try:
        file = repo.get_contents(FILE_PATH)
        csv_content = base64.b64decode(file.content).decode('utf-8')
        df = pd.read_csv(pd.compat.StringIO(csv_content))
        return df, file.sha
    except Exception:
        # If file doesn't exist or error occurs, create a new DataFrame
        return pd.DataFrame(columns=["id", "url"]), None

def append_url(url):
    """Append a new URL with a unique ID to the CSV and upload it"""
    df, file_sha = get_csv_content()
    
    # Generate unique ID
    unique_id = str(uuid.uuid4())[:8]
    
    # Append new data
    new_data = pd.DataFrame([[unique_id, url]], columns=["id", "url"])
    df = pd.concat([df, new_data], ignore_index=True)
    
    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False)
    
    # Upload to GitHub
    if file_sha:
        repo.update_file(FILE_PATH, "Updating CSV with new URL", csv_data, file_sha)
    else:
        repo.create_file(FILE_PATH, "Creating CSV with first entry", csv_data)

    print(f"URL {url} added successfully with ID {unique_id}")


    if url:
        append_url(url)
        st.success("url added")

        if st.button("Generate Report"):
            st.write("Generating Report...")
            # Create a new Word document
            doc = Document()
            doc.add_heading('NextQ.ai Report', level=1)
            doc.add_paragraph('This is the report for the NextQ.ai project.\n\n')
             # Save the document
            report_path = "NextQ_ai_Report.docx"
            doc.save(report_path)

            st.write("Report Generated Successfully!")
            st.write("Download the report from the link below:")

            # Provide download button
            with open(report_path, "rb") as file:
                st.download_button(
                    label="Download Report",
                    data=file,
                    file_name=report_path,
                    mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )

    else:
        st.warning("Please enter the URL to generate the report.")


