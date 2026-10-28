# logica/rag.py
import faiss
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar la API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ADVERTENCIA: No se encontró GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=API_KEY)

# El modelo de embeddings de Google
DIMENSIONES = 768 
indice_faiss = faiss.IndexFlatL2(DIMENSIONES)

textos_base = [
    "El proyecto maestro es un sistema de reconocimiento de patrones híbrido.",
    
]

def obtener_embedding(texto):
    """Llama a la API de Google para convertir texto en un vector matemático."""
    resultado = genai.embed_content(
        model="models/text-embedding-004",
        content=texto,
        task_type="retrieval_document"
    )
    # Convertir la lista de Python
    return np.array([resultado['embedding']], dtype='float32')

def cargar_conocimiento_inicial():
    """Vectoriza la base de datos de textos al arrancar el servidor."""
    print("Vectorizando base de conocimiento con Gemini...")
    for texto in textos_base:
        vector = obtener_embedding(texto)
        indice_faiss.add(vector)
    print("¡Conocimiento cargado en FAISS!")

# Ejecutar la carga al importar el módulo
cargar_conocimiento_inicial()

def generar_respuesta(pregunta_texto, usuario):
    """Busca contexto en FAISS y le pide a Gemini que redacte la respuesta final."""
    if indice_faiss.ntotal == 0:
        return "No tengo información en mi base de datos vectorial."

    # Convertir la pregunta en vector
    vector_pregunta = obtener_embedding(pregunta_texto)
    
    # Buscar el texto pre-guardado más similar matemáticamente
    distancias, indices = indice_faiss.search(vector_pregunta, k=1)
    indice_encontrado = indices[0][0]
    
    contexto_recuperado = textos_base[indice_encontrado] if indice_encontrado != -1 else "Sin contexto extra."

    # Armar el Prompt para la IA
    prompt = f"""
    Eres un asistente de voz inteligente de un proyecto universitario de ingeniería.
    El usuario identificado por biometría que te está hablando es: {usuario.capitalize()}.
    
    Pregunta del usuario: "{pregunta_texto}"
    
    Información de tu base de datos:
    {contexto_recuperado}
    
    Responde de forma amigable, directa y conversacional.
    """

    #  Generar la respuesta usando Gemini Flash
    modelo = genai.GenerativeModel('gemini-1.5-flash')
    respuesta = modelo.generate_content(prompt)
    
    return respuesta.text