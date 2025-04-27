import pytesseract
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import fitz  # PyMuPDF
import docx2txt
import os
import tempfile
import pdf2image
import easyocr
import numpy as np

from .models import OCRResponse



# Set up your Gemini API key
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(file_path):

    reader = easyocr.Reader(['en'], gpu=True)
    extracted_text = ""


    with tempfile.TemporaryDirectory() as path:
        images = pdf2image.convert_from_path(file_path, output_folder=path)

        for image in images:
            image = image.resize((int(image.width * 1.2), int(image.height * 1.2)))
            np_image = np.array(image)
            
            # OCR the image
            results = reader.readtext(np_image)

            for bbox, text, confidence in results:
                if confidence > 0.5: 
                    extracted_text += text.strip() + "\n"

    return extracted_text


# Function to extract text from a DOCX file
def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

# Function to extract text from an image using OCR
def extract_text_from_image(file_path):
    image = Image.open(file_path)

    image = image.convert("L")
    image = image.resize((int(image.width * 2), int(image.height * 2)))
    image = image.filter(ImageFilter.SHARPEN)
    image = ImageOps.autocontrast(image)  
    threshold = 130
    image = image.point(lambda p: 255 if p > threshold else 0)
    return pytesseract.image_to_string(image)

# Function to process extracted text with Gemini 
def process_with_gemini_direct(extracted_text: str, user_prompt: str) -> str:
    default_prompt = (
    "You are an expert document parser specializing in commercial documents like invoices, bills, and insurance papers.\n\n"
    "Extract the following structured data from the document text:\n"
    "- vendor_details: name, address, phone, email, website, PAN\n"
    "- customer_details: name, address, contact, PAN\n"
    "- invoice_details: bill_number, bill_date, transaction_date, mode_of_payment, finance_manager, authorized_signatory\n"
    "- payment_details: total, in_words, discount, taxable_amount, vat, net_amount\n"
    "- line_items (list): hs_code, description, qty, rate, amount\n\n"
    "Rules:\n"
    "1. Extract only the fields listed; do not guess or add extra fields.\n"
    "2. If a field is missing, set its value as `null`.\n"
    "3. Use context ('Vendor', 'Supplier', 'Bill To', 'Customer', etc.) to distinguish parties. If unclear, first business is vendor, second is customer.\n"
    "4. Each line_item must include hs_code and description; qty, rate, and amount are optional.\n"
    "5. Always return the result strictly in the following JSON structure:\n\n"
    "{\n"
    '  "vendor_details": {\n'
    '    "name": "...",\n'
    '    "address": "...",\n'
    '    "phone": "...",\n'
    '    "email": "...",\n'
    '    "website": "...",\n'
    '    "pan": "..."\n'
    '  },\n'
    '  "customer_details": {\n'
    '    "name": "...",\n'
    '    "address": "...",\n'
    '    "contact": "...",\n'
    '    "pan": "..."\n'
    '  },\n'
    '  "invoice_details": {\n'
    '    "bill_number": "...",\n'
    '    "bill_date": "...",\n'
    '    "transaction_date": "...",\n'
    '    "mode_of_payment": "...",\n'
    '    "finance_manager": "...",\n'
    '    "authorized_signatory": "..."\n'
    '  },\n'
    '  "payment_details": {\n'
    '    "total": ..., \n'
    '    "in_words": "...",\n'
    '    "discount": ..., \n'
    '    "taxable_amount": ..., \n'
    '    "vat": ..., \n'
    '    "net_amount": ...\n'
    '  },\n'
    '  "line_items": [\n'
    '    {\n'
    '      "hs_code": "...",\n'
    '      "description": "...",\n'
    '      "qty": "...",\n'
    '      "rate": "...",\n'
    '      "amount": "..."\n'
    '    }\n'
    '  ]\n'
    "}\n\n"
    "Important: Return ONLY the JSON object. No explanations, no headings, no extra text."
)

    # JSON format instruction is always appended
    json_instruction = "Return the type of document (eg.., inovice, bill payment)and results in structured JSON format only."

    # Choose either the user's prompt or the default
    active_prompt = user_prompt.strip() if user_prompt.strip() else default_prompt

    # Final prompt that always includes JSON formatting
    final_prompt = f"{active_prompt}\n\n{json_instruction}\n\nText:\n{extracted_text}"
    

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(final_prompt, generation_config=genai.types.GenerationConfig(
            temperature=0.2))
    return response.text

    # Main function to process the uploaded file
def process_file(file_path, user_prompt) -> OCRResponse:
    if file_path.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        extracted_text = extract_text_from_docx(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        extracted_text = extract_text_from_image(file_path)
    else:
        return OCRResponse(status="failed", message="Unsupported file type")

    structured_data = process_with_gemini_direct(extracted_text, user_prompt)    

    return OCRResponse(
        status="success",
        message="Text extracted and structured successfully",
        content=structured_data,
        extracted_text=extracted_text
    )
