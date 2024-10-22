import os
import streamlit as st
import google.generativeai as genai
import re
import csv
from pdf2image import convert_from_bytes
from PIL import Image
import time

api = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api)

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

output_path = "images"
output_file = "gemini_responses.csv"

def pdf_to_images(pdf_file, output_path):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        images = convert_from_bytes(pdf_file.read()) 
        
        for i, image in enumerate(images, start=1):
            image_path = os.path.join(output_path, f'page_{i}.jpg')
            image.save(image_path, 'JPEG')
        
        return len(images)  
    except Exception as e:
        st.write(f"Error converting PDF to images: {e}")
        return 0  

def delete_images(output_path):
    for filename in os.listdir(output_path):
        file_path = os.path.join(output_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith('.jpg'):
            os.remove(file_path)


def get_gemini_response(input_text, image, max_retries=3, delay_between_retries=5):
    for attempt in range(max_retries):
        try:
            response = model.generate_content([input_text, image])
            if response.candidates:
                content_parts = response.candidates[0].content.parts
                return " ".join(part.text for part in content_parts)  
            else:
                return None
        except Exception as e:
            if "429" in str(e):  
                st.write(f"Quota exceeded, retrying in {delay_between_retries} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay_between_retries)  
            else:
                st.write(f"Error: {e}")
                return None
    return None 

def extract_company_details(response):
    pattern = r".+?,.+?,.+?,.+"  
    matches = re.findall(pattern, response)
    matches = [match.split(",") for match in matches if len(match.split(",")) == 4]
    return matches

custom_inst = '''Extract company details including company names, email addresses, phone numbers, and website links in comma-separated format. Ensure accuracy and refrain from including any additional information beyond the CSV format.
Also do not read any timings and unnecessary things.

Desired Output Format:
Company name, Email address, Phone Number, Website

For Example(Do's):
Apple Inc., info@apple.com, +1-(800)-555-9876, www.apple.com
Google, info@google.com, +929168551364, www.google.com

(Dont's):
Apple Inc., info@apple.com, +1-(800)-555-9876, www.apple.com,something

Provide Only these 4 details.
Please provide only the necessary details as mentioned above. Do not include any additional information such as page numbers or any other extraneous content.
'''

st.title("Company Details Extractor")


pdf_files = st.file_uploader("Choose pdf files...", type="pdf", accept_multiple_files=True)

if pdf_files:
    for pdf_file in pdf_files:
        
        total_pages = pdf_to_images(pdf_file, output_path)
        
        if total_pages == 0:
            st.write("Error processing PDF file.")
            continue
        
        st.write(f"Processing {total_pages} pages.")

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Company Name", "Email Address", "Phone Number", "Website"])  # CSV Header

        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)

            for filename in os.listdir(output_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    st.write(f"Processing page: {filename}")
                    image_path = os.path.join(output_path, filename)
                    image = Image.open(image_path)

                
                    img_response = get_gemini_response(custom_inst, image)

                    if img_response:
                        company_details = extract_company_details(img_response)

                        for detail in company_details:
                            csvwriter.writerow(detail)  
                    else:
                        st.write(f"No valid response for page {filename}.")

        delete_images(output_path)  

        st.write(f"All responses saved to CSV file: {output_file}")
