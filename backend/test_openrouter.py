from dotenv import load_dotenv
load_dotenv()

from app.services.openai_client import get_client, get_model

client = get_client()
model = get_model()

response = client.chat.completions.create(
    model=model,
    temperature=0,
    messages=[
        {"role": "system", "content": "Return JSON only"},
        {"role": "user", "content": "Return {\"status\": \"ok\"}"}
    ]
)

print(response.choices[0].message.content)
