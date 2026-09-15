import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

raw_input = """Hola Hola Hola cómo Hola cómo estás Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito comprar Hola Cómo estás Necesito comprar Hola Cómo estás Necesito comprar lec Hola Cómo estás Necesito comprar lechu Hola Cómo estás Necesito comprar lechuga Hola Cómo estás Necesito comprar lechuga toma Hola Cómo estás Necesito comprar lechuga tomate Hola Cómo estás Necesito comprar lechuga tomate Hola Cómo estás Necesito comprar lechuga tomate  2  2 kg  2 kg de  2 kg de toma  2 kg de tomate  2 kg de tomate  2 kg de tomate  2 kg de tomate  2 kg de tomate"""

if client:
    prompt = f"""Analizá la siguiente transcripción de dictado por voz o mensaje de WhatsApp.
El texto contiene muletillas, tartamudeos o palabras/frases repetidas debido al reconocimiento de voz.

TEXTO TRANSCRITO:
\"\"\"{raw_input}\"\"\"

Tu tarea:
1. Eliminar repeticiones, saludos (hola, cómo estás), frases cortadas y muletillas.
2. Identificar productos para la lista de compras (categorías validas: 'supermercado', 'verduleria', 'ferreteria', 'farmacia'), separando nombre del producto y cantidad si se especifica (ej: '2 kg').
3. Identificar turnos o eventos para el calendario.
4. Identificar avisos o notas importantes.

Devuelve EXCLUSIVAMENTE un objeto JSON válido con esta estructura:
{{
  "shopping": [
    {{"name": "Lechuga", "quantity": "1 kg", "category": "verduleria"}}
  ],
  "calendar": [
    {{"title": "Evento", "category": "servicio", "due_date": "YYYY-MM-DD"}}
  ],
  "notices": [
    {{"content": "Aviso"}}
  ]
}}"""

    try:
        for model_name in ['gemini-2.5-flash']:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json',
                        temperature=0.1
                    )
                )
                print(f"RESPUESTA IA CON {model_name}:")
                print(response.text)
                break
            except Exception as e:
                print(f"Error con {model_name}: {e}")
    except Exception as e:
        print("Error:", e)
else:
    print("Client no disponible")
