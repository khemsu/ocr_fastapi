from pydantic import BaseModel

class OCRResponse(BaseModel):
    status: str
    message: str
    content: str
    extracted_text: str
