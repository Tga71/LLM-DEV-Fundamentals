import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Initialization
load_dotenv()

# Configuration
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
selected_model="gpt-4o-mini"
system_message="You are a helpful assistant."

# Prompt
prompt = "Explain what a temperature in LLMs means in one paragraph."

# Message
completion = client.chat.completions.create(
    model=selected_model,
    messages=[
        {
            "role": "system", 
            "content": system_message
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    max_tokens=200
)

# Output
print("===============")
print(completion.choices[0].message.content)
print("===============")

