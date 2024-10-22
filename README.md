**Company Details Extractor :**
This is a Streamlit web application that extracts company details including company names, email addresses, phone numbers, and website links from PDF files or images using the Google Generative AI API.

**Setup :**
git clone https://github.com/AhamadAshiq/company_details_extractor.git

**Set .env file**

**Install Poppler**
https://github.com/oschwartz10612/poppler-windows/releases

Add it in env variables
Steps:
Go to Control Panel > System and Security> System
Click on Advanced system settings
Click on Environment Variables
Under System Variables, scroll down and find the Path variable, click Edit.
Click New and enter the path to the Poppler binaries (e.g., C:\Program Files\)

**Install the required dependencies :**
streamlit
google-generativeai
pandas
Pillow
pdf2image

**Run the webapp :**
streamlit run app.py


