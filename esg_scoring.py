from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from tika import parser
import re
import pandas as pd
import requests
from typing import Dict

# Load ESG-BERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("nbroad/ESG-BERT")
model = AutoModelForSequenceClassification.from_pretrained("nbroad/ESG-BERT")
classifier = pipeline('text-classification', model=model, tokenizer=tokenizer)

# PDF parsing class
class PDFParser:
    def __init__(self, pdf_content: bytes):
        self.raw = parser.from_buffer(pdf_content)
        self.text = self.raw.get('content', '')

    def get_text_clean_list(self):
        text = re.sub(r'\n', ' ', self.text)
        text = re.sub(r'\s+', ' ', text)
        return text.split('.')

# Function to analyze ESG scores from a PDF URL
def analyze_pdf_url(pdf_url: str) -> Dict[str, float]:
    response = requests.get(pdf_url)
    response.raise_for_status()
    
    pdf_parser = PDFParser(response.content)
    sentences = pdf_parser.get_text_clean_list()
    
    result = classifier(sentences)
    df = pd.DataFrame(result)
    score_summary = df.groupby(['label'])['score'].mean().to_dict()
    
    return {"scores": score_summary, "sentence_count": len(sentences)}
