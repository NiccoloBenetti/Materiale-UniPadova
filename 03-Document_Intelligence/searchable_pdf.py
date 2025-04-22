'''
Source:
https://github.com/christopherwoodland/Searchable-PDF/tree/main

with minimum refactoring for reading endpoint and key from environment variables.

NB:
Requires a Document Intelligence SINGLE-SERVICE deployment in Azure.

To launch this script, go to the terminal of your compute and launch "python searchable_pdf.py"

'''

import base64
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='../infra/credentials.env', override=True)

# Read endpoint and key from environment variables
DOC_INTEL_URL = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
DOC_INTEL_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

def encode_pdf_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
    return encoded_string

def call_api(encoded_pdf):
    url = f"{DOC_INTEL_URL}/documentintelligence/documentModels/prebuilt-read:analyze"
    params = {
        "_overload": "analyzeDocument",
        "output": "pdf",
        "api-version": "2024-07-31-preview"
    }
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": DOC_INTEL_KEY  # Use the key from environment variables
    }
    body = {
        "base64Source": encoded_pdf
    }
    response = requests.post(url, headers=headers, params=params, json=body)
    if response.status_code == 202:
        # the request has been accepted for processing but is not yet completed
        request_id = response.headers.get('apim-request-id')
        return poll_status(request_id, pdf_path)
    return response.json()

def poll_status(request_id, pdf_path):
    status_url = f"{DOC_INTEL_URL}/documentintelligence/documentModels/prebuilt-read/analyzeResults/{request_id}?api-version=2024-07-31-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": DOC_INTEL_KEY  # Use the key from environment variables
    }
    while True:
        response = requests.get(status_url, headers=headers)
        result = response.json()
        if result.get("status") == "succeeded":
            return get_file(request_id, pdf_path)
        time.sleep(10)

def get_file(request_id, pdf_path):
    file_url = f"{DOC_INTEL_URL}/documentintelligence/documentModels/prebuilt-read/analyzeResults/{request_id}/pdf?api-version=2024-07-31-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": DOC_INTEL_KEY  # Use the key from environment variables
    }
    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = f"{base_name}_search.pdf"
        with open(output_file, "wb") as file:
            file.write(response.content)
        return f"File downloaded successfully as {output_file}"
    return response.json()

if __name__ == "__main__":
    print(DOC_INTEL_URL)
    # print(DOC_INTEL_KEY)
    pdf_path = r"invoice_sample.jpg"  # Replace with the path to your PDF file
    encoded_pdf = encode_pdf_base64(pdf_path)  # Encode the PDF with BASE64
    result = call_api(encoded_pdf)
    print(result)