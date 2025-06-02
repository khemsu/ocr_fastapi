# ocr_fastapi

## Overview
`ocr_fastapi` is a Python-based web application designed to perform Optical Character Recognition (OCR) on uploaded documents (PDFs, DOCX, and common image formats). It then extracts structured information from these documents, with a specialization in commercial documents like invoices and bills.

## Key Features
- **Document Upload:** Users can upload documents (PDF, DOCX, PNG, JPG, JPEG) through a web interface.
- **Text Extraction:** The application extracts raw text from these documents using appropriate libraries for each file type.
- **Structured Data Extraction:** Utilizes Google's Gemini 2.0 language model (via Langchain) to parse the extracted text and structure it into a predefined JSON format. This is particularly tailored for commercial documents, identifying fields such as vendor details, customer details, invoice information, and line items.
- **API-Driven:** Built with FastAPI, providing an API endpoint for document processing.
- **Web Interface:** Basic HTML frontend for uploading files and viewing results.
- **Alternative OpenAI Integration:** Includes an (currently inactive) module for processing with OpenAI's GPT models.

## Technologies Used
- **Backend Framework:** FastAPI, Uvicorn
- **OCR & Document Processing:**
    - PyTesseract (for images)
    - PyPDFLoader (Langchain wrapper for PyMuPDF, for PDFs)
    - docx2txt (for DOCX files)
    - Pillow (for image manipulation)
- **AI/Language Models:**
    - Google Gemini 2.0
    - Langchain (for LLM orchestration, prompt management, and document loading)
- **Data Handling & Validation:** Pydantic
- **Templating:** Jinja2 (for the HTML interface)
- **Environment Management:** python-dotenv
- **Core Language:** Python

## Setup and Installation (Placeholder)
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ocr_fastapi
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   - Create a `.env` file in the `backend` directory.
   - Add your `GEMINI_API_KEY` and, if you plan to use it, your `OPENAI_API_KEY`:
     ```env
     GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
     # OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
     ```
5. **(If Tesseract is not installed system-wide) Install Tesseract OCR:**
   - Follow instructions for your OS: [https://tesseract-ocr.github.io/tessdoc/Installation.html](https://tesseract-ocr.github.io/tessdoc/Installation.html)

## Usage (Placeholder)
1. **Run the application:**
   ```bash
   python run.py
   ```
   Or, using Uvicorn directly (from the repository root, assuming `run.py` targets `backend.main:app`):
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
2. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:8000`.
3. **Upload a document** and provide an optional prompt to guide the extraction.
4. View the extracted text and structured JSON output.
