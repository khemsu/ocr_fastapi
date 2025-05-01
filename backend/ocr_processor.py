import os
from PIL import Image, ImageFilter, ImageOps
import pytesseract
import docx2txt
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from .models import OCRResponse


from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


template = (
    "You are an expert document parser specializing in commercial documents like invoices, bills, and insurance papers.\n\n"
    "Extract the following structured data from the document text:\n"
    "- vendor_details: name, address, phone, email, website, PAN\n"
    "_customer_details: name, address, contact, PAN usually below vendor_details\n"
    "- invoice_details: bill_number, bill_date, transaction_date, mode_of_payment, finance_manager, authorized_signatory\n"
    "- payment_details: total, in_words, discount, taxable_amount, vat, net_amount\n"
    "- line_items (list): hs_code, description, qty, rate, amount\n\n"
    "Rules:\n"
    "1. Extract only the fields listed; do not guess or add extra fields.\n"
    "2. If a field is missing, set its value as null.\n"
    "3. Use context ('Vendor', 'Supplier', 'Bill To', 'Customer', etc.) to distinguish parties. If unclear, first business is Vendor, second is Customer.\n"
    "4. Each line_item must include hs_code and description; qty, rate, and amount are optional.\n"
    "5. Always return the result strictly in the following JSON structure:\n"
    "6. PAN numbers are typically boxed or near labels like 'PAN No.', and follow a 9-digit (Nepal) format.\n\n"
    "{{\n"
    '  "vendor_details": {{\n'
    '    "name": "...",\n'
    '    "address": "..."(use commas as separators),\n'
    '    "phone": "..."(eg: +977-1-XXXXXXX, +977-XXXXXXXXXX, or 01-XXXXXXX)\n'
    '    "email": "...",\n'
    '    "website": "...",\n'
    '    "pan": "..."\n'
    '  }},\n'
    '  "customer_details": {{\n'
    '    "name": "...",\n'
    '    "address": "...",\n'
    '    "contact": "...",\n'
    '    "pan": "..."\n'
    '  }},\n'
    '  "invoice_details": {{\n'
    '    "bill_number": "...",\n'
    '    "bill_date": "...",\n'
    '    "transaction_date": "...",\n'
    '    "mode_of_payment": "...",\n'
    '    "finance_manager": "...",\n'
    '    "authorized_signatory": "..."\n'
    '  }},\n'
    '  "payment_details": {{\n'
    '    "total": ..., \n'
    '    "in_words": "...",\n'
    '    "discount": ..., \n'
    '    "taxable_amount": ..., \n'
    '    "vat": ..., \n'
    '    "net_amount": ...\n'
    '  }},\n'
    '  "line_items": [\n'
    '    {{\n'
    '      "hs_code": "...",\n'
    '      "description": "...",\n'
    '      "qty": "...",\n'
    '      "rate": "...",\n'
    '      "amount": "..."\n'
    '    }}\n'
    '  ]\n'
    "}}\n\n"
    "Important: Return ONLY the JSON object. No explanations, no headings, no extra text.\n\n"
    "Document text:\n{text}"
)

prompt = PromptTemplate.from_template(template)
llm = ChatGoogleGenerativeAI(model="gemini-2.0",google_api_key=GEMINI_API_KEY )
chain = LLMChain(llm=llm, prompt=prompt)


def extract_text_from_image(file_path):
    image = Image.open(file_path).convert("L")
    image = image.resize((image.width * 2, image.height * 2))
    image = image.filter(ImageFilter.SHARPEN)
    threshold = 130
    image = image.point(lambda p: 255 if p > threshold else 0)
    return pytesseract.image_to_string(image)


def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)


def extract_text_from_pdf(file_path):
    
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    return "\n".join([page.page_content for page in pages])

# Unified processor using LangChain chain
def process_file(file_path, user_prompt="") -> OCRResponse:
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        text = extract_text_from_image(file_path)
    else:
        return OCRResponse(status="failed", message="Unsupported file type")

    result = chain.run({"text": text})
    
    return OCRResponse(
        status="success",
        message="Text extracted and structured successfully",
        content=result,
        extracted_text=text
    )
