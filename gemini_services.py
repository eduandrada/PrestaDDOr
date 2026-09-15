import os
import base64
from io import BytesIO
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def chat_ia(prompt: str, rol: str = "asesor") -> str:
    """Atiende al Asesor IA y al Contador IA según el rol."""
    if not client:
        return "Clave de Gemini API no configurada."

    instrucciones = {
        "asesor": "Sos el Asesor IA de préstamos y cobranzas. Respondé de forma concisa, analítica y directa.",
        "contador": "Sos el Contador IA experto en tasas reales, flujo de caja y balances contables en pesos argentinos."
    }
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=instrucciones.get(rol, instrucciones["asesor"]),
                temperature=0.3
            )
        )
        return response.text
    except Exception as e:
        return f"Error al generar respuesta IA: {str(e)}"

def generar_cv_ia(datos_usuario: str) -> str:
    """Genera un CV profesional formateado en Markdown / HTML para el Convertidor Universal."""
    if not client:
        return "Error: Falta GEMINI_API_KEY"

    prompt = f"""Con los siguientes datos, redactá un Curriculum Vitae profesional, optimizado y moderno:
    {datos_usuario}
    Formatealo de manera limpia en Markdown (o secciones estructuradas listas para imprimir)."""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error al redactar CV con IA: {str(e)}"

def generar_imagen_sorteo(descripcion_premio: str) -> str:
    """Genera un banner/flyer publicitario del sorteo y devuelve la imagen en Base64."""
    if not client:
        return None

    prompt = f"Flyer promocional vibrante para sorteo de rifa o bingo: {descripcion_premio}. Estilo publicitario profesional, colores llamativos, render 3D hiperrealista, composición centrada."
    
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=dict(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )
        
        for img in result.generated_images:
            return base64.b64encode(img.image.image_bytes).decode("utf-8")
    except Exception as e:
        print(f"Error generando imagen de sorteo con Imagen 3: {e}")
        
    return None

def escaneo_camscanner_ia(imagen_bytes: bytes, formato_salida: str = "docx") -> str:
    """Procesa una imagen de recibo/pagaré con Gemini 2.5 Vision para extraer texto y estructura."""
    if not client:
        return "Error: Clave de Gemini API no configurada."

    prompt = f"""Sos un escáner OCR profesional CamScanner de alta precisión.
Analizá minuciosamente esta imagen (pagaré, recibo, factura o documento).
Extraé y transcribí todo el texto, importes en pesos/dólares, fechas, nombres de clientes/firmantes y detalles.
Formatealo de manera limpia y estructurada para exportar a {formato_salida.upper()}."""

    try:
        image_part = types.Part.from_bytes(
            data=imagen_bytes,
            mime_type="image/jpeg"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image_part, prompt]
        )
        return response.text
    except Exception as e:
        return f"Error en escaneo OCR con Gemini IA: {str(e)}"

