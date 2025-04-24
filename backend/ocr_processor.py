import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import docx2txt
from .models import OCRResponse
import os

# Set up your Gemini API key
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Function to extract text from a PDF
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to extract text from a DOCX file
def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

# Function to extract text from an image using OCR
def extract_text_from_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

# Function to process extracted text with Gemini 
def process_with_gemini_direct(extracted_text: str, user_prompt: str) -> str:
    
    prompt = (
        
        f"{user_prompt.strip()}\n\n" #strip() removes trailing or leading characters from a string
        f"Text:\n{extracted_text}"
    )

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(
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
