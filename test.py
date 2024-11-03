import boto3
import json
import base64
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF text extraction

load_dotenv()

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')


prompt = """Analyse le rapport annuel de l'entreprise pour identifier les informations clés sur sa performance financière, ses risques principaux, et ses perspectives de croissance. Concentre-toi sur les sections qui décrivent les indicateurs financiers, les déclarations de la direction, les stratégies futures, et les éléments de risque mentionnés. Fournis un résumé structuré en expliquant :
- Les performances et résultats financiers récents
- Les stratégies et initiatives de croissance
- Les risques principaux identifiés par l'entreprise
- Toute mention des tendances économiques ou du marché qui peuvent influencer ses opérations.

Peux-tu extraire les ratios financiers principaux tels que le ratio de liquidité et le ratio d'endettement? Indique également les initiatives de développement durable mentionnées dans le rapport."""


pdf_path = "2023-CN-Rapport-Annuel.pdf"

# Extract text from PDF using PyMuPDF
pdf_text = ""
with fitz.open(pdf_path) as pdf_file:
    for page_num in range(pdf_file.page_count):
        page = pdf_file[page_num]
        pdf_text += page.get_text()

# Truncate if the text is too long
max_length = 1000  # Adjust this value based on model limits
pdf_text = pdf_text[:max_length]
prompt = f"{pdf_text}. Additionally, {prompt}"



kwargs = {
    "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
    "contentType": "application/json",
    "accept": "application/json",
    "body": json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
}

response = bedrock_runtime.invoke_model(**kwargs)

body = json.loads(response['body'].read())

print(body)
