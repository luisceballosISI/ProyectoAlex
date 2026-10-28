from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
import os
from logica.biometria import identificar_usuario
from logica.rag import generar_respuesta
from logica.audio_utils import transcribir_audio, texto_a_audio

app = FastAPI()

# 1. Crear carpeta static si no existe y montarla para que el ESP32 pueda descargar el MP3
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Administrador de la conexión con el ESP32
esp32_connection = None

@app.websocket("/ws/esp32")
async def websocket_esp32(websocket: WebSocket):
    global esp32_connection
    await websocket.accept()
    esp32_connection = websocket
    print("ESP32 conectado y esperando audio...")
    try:
        while True:
            # Mantener la conexión viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        esp32_connection = None
        print("ESP32 desconectado")

@app.post("/api/hablar")
async def recibir_audio_pc(archivo: UploadFile = File(...)):
    global esp32_connection
    
    # 1. Leer el audio de la PC
    datos_audio = await archivo.read()
    
    # 2. Biometría: ¿Quién habla?
    usuario = identificar_usuario(datos_audio)
    print(f"Usuario detectado: {usuario}")
    
    # 3. STT: ¿Qué dijo?
    pregunta = transcribir_audio(datos_audio)
    print(f"Pregunta transcrita: {pregunta}")
    
    # Corrección de sintaxis: "not" en lugar de "no"
    if not pregunta:
        return {"status": "No se entendió el audio"}

    # 4. RAG + IA: Generar respuesta inteligente
    respuesta_texto = generar_respuesta(pregunta, usuario)
    print(f"IA responde: {respuesta_texto}")
    
    # 5. TTS: Convertir respuesta a voz y GUARDAR EL ARCHIVO MP3
    audio_respuesta = texto_a_audio(respuesta_texto)
    ruta_mp3 = "static/respuesta.mp3"
    with open(ruta_mp3, "wb") as f:
        f.write(audio_respuesta)
    
    # 6. Enviar señal de TEXTO al ESP32 para que reproduzca el archivo
    if esp32_connection:
        await esp32_connection.send_text("REPRODUCIR")
        print("Aviso enviado al ESP32 exitosamente.")
    else:
        print("Advertencia: El ESP32 no está conectado al WebSocket.")
        
    return {"usuario": usuario, "pregunta": pregunta, "respuesta": respuesta_texto}