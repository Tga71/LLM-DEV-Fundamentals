import os
from dotenv import load_dotenv
from openai import OpenAI

# Initialization
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration
client = OpenAI(api_key=API_KEY)
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

