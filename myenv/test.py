import boto3
import json

# Create a Bedrock runtime client in the 'us-west-2' Region
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2"
)

prompt = 'where are you located'

kwargs = {
  "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
  "contentType": "application/json",
  "accept": "application/json",
  "body": json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 200,
    "top_k": 250,
    "stop_sequences": [],
    "temperature": 1,
    "top_p": 0.999,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt
          }
        ]
      }
    ]
  })
}

# Invoke the model using the bedrock_runtime client
response = bedrock_runtime.invoke_model(**kwargs)

# Read and decode the response body content
response_body = response['body'].read().decode('utf-8')
response_data = json.loads(response_body)  # Load it as JSON if it's in JSON format

# Print the response data
print(response_data)
