import requests
from bs4 import BeautifulSoup
import json
import re
import boto3
import webbrowser  # Ensure this is imported to handle opening URLs in the browser
from dotenv import load_dotenv

def download_and_analyze_sec_document(cik, year, form_type, isLink):
    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    headers = {'User-Agent': 'MyFinApp/1.0 (contact@mydomain.com)'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        filings = data.get("filings", {}).get("recent", {})

        for i, form in enumerate(filings.get("form", [])):
            if form == form_type and filings["filingDate"][i].startswith(str(year)):
                accession_number = filings["accessionNumber"][i].replace("-", "")
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{filings['primaryDocument'][i]}"

                # Open in browser if isLink is True
                if isLink:
                    print(f"Opening HTML document in a new browser tab: {filing_url}")
                    webbrowser.open(filing_url)

                # Download HTML content
                filing_page = requests.get(filing_url, headers=headers)
                html_filename = f"{cik}_{form_type}_{year}.html"
                with open(html_filename, 'wb') as file:
                    file.write(filing_page.content)
                print(f"Downloaded HTML: {html_filename}")

                # Read HTML content for analysis
                with open(html_filename, 'r', encoding='utf-8') as file:
                    html_text = file.read()

                # Choose prompt based on form_type
                if form_type == "DEF 14A":
                       prompt = """Review this proxy statement to extract information on:
                        - Board of Directors composition and structure.
                        - Executive compensation details.
                        - Major shareholders and their influence.
                        - Governance practices and any proposals that impact policy."""
                
                elif form_type == "8-K":
                   prompt = """Examine this 8-K report to provide a summary of:
                        - Significant recent events (e.g., leadership changes, transactions).
                        - Any major financial updates or critical announcements.
                        - Immediate strategic implications for the company."""
                
                elif form_type == "10-K":
                    
                    prompt = """Provide a comprehensive analysis of the annual report focusing on:
                        - Key financial performance, with specific figures for principal assets and liabilities (e.g., Derivative Assets, Other Current and Noncurrent Assets, and Liabilities).
                        - Major highs and lows in recent years.
                        - Information on any borrowing for growth or issuance of new shares, with amounts where available.
                        - The companys ability to cover short-term liabilities based on its assets.
                        - Dividend performance versus capital gains focus.
                        - Whether the company is conserving cash for acquisitions, specifying which if applicable.
                        - Evidence of growth potential, supported by specific financial indicators.
                        - Changes in operating costs and their impact, especially if costs are rising without sales growth.
                        - Managements strategic objectives, revenue trends, risks, growth opportunities, and outlook.
                        Ensure that the analysis includes specific numbers and financial data where present in the text."""
                
                elif form_type == "10-Q":
                  
                     prompt = """Analyze this quarterly report to provide insights on:
                        - Short-term performance indicators.
                        - Any changes in costs or revenue, and implications for overall performance.
                        - Key updates on risks or market changes.
                        - Adjustments in financial guidance or forecasts if present."""
                
               
                else:
                    prompt = """Provide a high-level analysis of this filing, emphasizing:
                        - Key financial or strategic insights.
                        - Stakeholder implications.
                        - Any critical updates on operations or market positioning."""


                # Load environment variables and configure AWS client
                load_dotenv()
                bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

                # Call the AI model
                kwargs = {
                    "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
                    "contentType": "application/json",
                    "accept": "application/json",
                    "body": json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 1000,
                        "messages": [{"role": "user", "content": prompt}]
                    })
                }

                response = bedrock_runtime.invoke_model(**kwargs)
                body = json.loads(response['body'].read())
                print("Analysis Result:", body)
                return
            


def get_cik_from_claude(ticker):
    load_dotenv()
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
    prompt = f"What is the Central Index Key (CIK) number for the company with the ticker symbol '{ticker}' from https://www.sec.gov/Archives/edgar? Please only give the 0000 followed by the CIK and say nothing more or less. This is very important, if you say one letter more or less it will be detrimental, give only the CIK."

    kwargs = {
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,  # Adjust token limit as needed
            "messages": [{"role": "user", "content": prompt}]
        })
    }

    response = bedrock_runtime.invoke_model(**kwargs)
    body = json.loads(response['body'].read())

    # Debug: Print the whole body to verify structure
    # print("Response body:", json.dumps(body, indent=2))

    if 'content' in body:
        # Assuming content is directly under the root and is a list
        cik_text = body['content'][0]['text'] if body['content'] else 'No CIK found'
        print("Found CIK:", cik_text)
        return cik_text
    else:
        print("No 'content' key or no content in the response")

    return None

OpenLink= True
year=2024
formtype ="8-K"
cik = get_cik_from_claude("MSFT")
# Example usage
download_and_analyze_sec_document(cik, year,formtype,OpenLink)  # Replace with desired CIK, year, and form type.
