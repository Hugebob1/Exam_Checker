from llama_cpp import Llama

llm = Llama(
    model_path="C:/Users/aleks/Bielik-11B-v2.3-Instruct.Q4_K_M.gguf",
    n_ctx=2048,      # wielkość "pamięci" modelu (kontekst)
    n_threads=6,     # zmień na liczbę swoich rdzeni procesora (zostaw 1-2 wolne dla systemu)
    n_gpu_layers=0   # WYMUSZENIE pracy na samym procesorze (CPU)
)

print("--- Bielik gotowy do pracy (Tryb CPU) ---")

prompt = "Wymień 3 najciekawsze miejsca w Polsce na wakacje i krótko je uzasadnij."

response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "Jesteś uprzejmym asystentem, który odpowiada konkretnie i po polsku."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7, # kreatywność (0.1 - sztywny, 0.9 - bardzo kreatywny)
    max_tokens=500   # maksymalna długość odpowiedzi
)

# 3. Wyświetl odpowiedź
print("\nOdpowiedź Bielika:")
print(response["choices"][0]["message"]["content"])