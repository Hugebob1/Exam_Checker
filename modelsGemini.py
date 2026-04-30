import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

print("--- TWOJE DOSTĘPNE MODELE (PODEJŚCIE NR 3) ---")

try:
    for model in client.models.list():
        # Wyciągamy ID modelu (np. gemini-3-pro)
        m_id = model.name.split('/')[-1]

        # Sprawdzamy supported_actions zamiast supported_methods
        if hasattr(model, 'supported_actions'):
            actions = model.supported_actions
            # Szukamy czy model potrafi generować treść
            if "generate_content" in actions or "generateContent" in actions:
                print(f"MODEL ID: {m_id}")
                print(f"OPIS:     {model.display_name}")
                print("-" * 40)
except Exception as e:
    # Jeśli to znowu sypnie błędem, to wypiszemy surowe obiekty, żebyś widział co tam jest
    print(f"Coś poszło nie tak: {e}")
    print("\nSUROWA LISTA (Wszystko co masz na koncie):")
    for m in client.models.list():
        print(f"Nazwa: {m.name}")