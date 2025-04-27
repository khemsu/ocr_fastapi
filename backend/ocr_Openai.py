# import openai
# from openai import OpenAI
# import os
# import pytesseract
# from PIL import Image
# import fitz  # PyMuPDF
# import docx2txt
# from .models import OCRResponse


# # Load environment variables
# from dotenv import load_dotenv
# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# # Extract text from different file types
# def extract_text_from_pdf(file_path):
#     text = ""
#     with fitz.open(file_path) as doc:
#         for page in doc:
#             text += page.get_text()
#     return text

# def extract_text_from_docx(file_path):
#     return docx2txt.process(file_path)

# def extract_text_from_image(file_path):
#     image = Image.open(file_path)
#     return pytesseract.image_to_string(image)

# # Process with OpenAI chat model
# def process_with_openai_chat(extracted_text: str, user_prompt: str) -> str:
#     default_prompt = (
#         "You are a reliable and intelligent document parser specialized in processing invoices.\n"
#         "Your task is to extract only the following fields from the document:\n"
#         "- vendor Name\n"
#         "- vendor Address\n"
#         "- vendor regd. no\n"
#         "- transaction type\n"
#         "- transaction no.\n"
#         "- document number\n"
#         "- posting date\n"
#         "- due date\n"
#         "- document date\n"
#         "- nepali miti\n"
#         "- lc no.\n\n"
#         "Strictly follow these rules:\n"
#         "1. Only extract the exact fields listed above. Do not infer or guess unrelated fields.\n"
#         "2. If a field is not found or not explicitly mentioned in the document, return its value as `null`.\n"
#         "3. Do not hallucinate or fabricate any values.\n"
#         "4. Return the result as a valid JSON object with the following structure:\n"
#         "{\n"
#         '  "document_type": "Invoice",\n'
#         '  "fields": {\n'
#         '    "vendor Name": ...,\n'
#         '    "vendor Address": ...,\n'
#         '    "vendor regd. no": ...,\n'
#         '    "transaction type": ...,\n'
#         '    "transaction no.": ...,\n'
#         '    "document number": ...,\n'
#         '    "posting date": ...,\n'
#         '    "due date": ...,\n'
#         '    "document date": ...,\n'
#         '    "nepali miti": ...,\n'
#         '    "lc no.": ...\n'
#         '  }\n'
#         "}\n"
#         "Make sure the output is strictly in valid JSON format and contains no explanation, notes, or extra text—only the JSON object."
#     )

#     json_instruction = "Return the type of document (e.g., invoice, bill payment) and results in structured JSON format only."
#     active_prompt = user_prompt.strip() if user_prompt.strip() else default_prompt
#     final_prompt = f"{active_prompt}\n\n{json_instruction}\n\nText:\n{extracted_text}"

#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",  # or gpt-4 if you have access
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": final_prompt}
#         ],
#         temperature=0.2
#     )

#     return response.choices[0].message.content

# # Main function to process the file
# def process_file(file_path, user_prompt) -> OCRResponse:
#     if file_path.endswith(".pdf"):
#         extracted_text = extract_text_from_pdf(file_path)
#     elif file_path.endswith(".docx"):
#         extracted_text = extract_text_from_docx(file_path)
#     elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
#         extracted_text = extract_text_from_image(file_path)
#     else:
#         return OCRResponse(status="failed", message="Unsupported file type")

#     structured_data = process_with_openai_chat(extracted_text, user_prompt)

#     return OCRResponse(
#         status="success",
#         message="Text extracted and structured successfully",
#         content=structured_data,
#         extracted_text=extracted_text
#     )
