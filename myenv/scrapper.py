from flask import Flask, request, jsonify
import boto3
import json
import pandas as pd
from io import StringIO

app = Flask(__name__)

# Define the Get_opinion function

def Get_opinion(input):
    # Initialize S3 and Bedrock runtime clients
    s3 = boto3.client('s3')
    bedrock_runtime = boto3.client('bedrock-runtime', region_name="us-west-2")

    # S3 bucket and file names
    bucket_name = "webscrapper2"
    data_file_key = "data.csv"
    urls_content_file_key = "urls_contents.csv"

    # Function to read CSV from S3
    def read_csv_from_s3(bucket, key):
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return pd.read_csv(StringIO(content))

    # Load data from both CSV files
    data_df = read_csv_from_s3(bucket_name, data_file_key)
    urls_content_df = read_csv_from_s3(bucket_name, urls_content_file_key)

    # Filter for mentions of "Apple stock"
    apple_mentions_data = data_df[data_df.apply(lambda row: row.astype(str).str.contains(input, case=False).any(), axis=1)]
    apple_mentions_urls_content = urls_content_df[urls_content_df.apply(lambda row: row.astype(str).str.contains(input, case=False).any(), axis=1)]

    # Combine relevant content into a single text
    apple_insights = "\n".join(apple_mentions_data.astype(str).apply(" | ".join, axis=1).values.tolist())
    apple_insights += "\n" + "\n".join(apple_mentions_urls_content.astype(str).apply(" | ".join, axis=1).values.tolist())

    # Prompt for Claude
    prompt = f"Based on the following information about Apple stock, what do people think about it?\n\n{apple_insights}"

    # Set up Bedrock request
    kwargs = {
        "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    }

    # Invoke the model using the Bedrock runtime client
    response = bedrock_runtime.invoke_model(**kwargs)

    # Read and decode the response body content
    response_body = response['body'].read().decode('utf-8')
    response_data = json.loads(response_body) # Load as JSON if it's in JSON format

    # Print the response data
    print(response_data)
    return response_data

# Define the endpoint to receive requests from the frontend
@app.route('/analyze_csv_from_s3', methods=['POST'])
def analyze_csv_from_s3():
    data = request.get_json()
    query = data.get("query")
    
    print("Query received:", query)  # Debugging line: log the received query

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Call Get_opinion function with the query
    result = Get_opinion(query)
    
    # Extract summary from result or handle error response
    summary = result.get("content", {}).get("text", "No relevant information found.") if result else "Error processing request."

    print("Summary generated:", summary)  # Debugging line: log the summary generated

    # Return the response to the frontend
    return jsonify({"summary": summary})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
