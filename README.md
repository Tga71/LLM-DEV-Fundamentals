# LLM-DEV-Fundamentals

## Setup
1. Run in terminal:
```sh
python -m venv venv
```

2. If not activated automatically in editor, activate venv
```sh
venv\Scripts\activate
```

3. Install dependencies
```sh
python -m pip install -r requirements.txt
```

4. Move .env.example to .env and save your API key
Token can be created here: https://platform.openai.com/api-keys
Good practice is to limit your spending here: https://platform.openai.com/settings/organization/limits

5. Test your connection
```sh
python src/01_simple_message.py
```

## Errors

### 409 - You exceeded your current quota, please check your plan...
Top off your account here: https://platform.openai.com/settings/organization/billing/overview and create new API Key