# cliente_pc.py
import sounddevice as sd
import wave
import io
import requests

def grabar_y_enviar():
    url = "http://127.0.0.1:8000/api/hablar"
    frecuencia = 16000
    duracion = 5  # Segundos para hablar
    
    input("Presiona ENTER para hablar...")
    print("🔴 GRABANDO...")
    grabacion = sd.rec(int(duracion * frecuencia), samplerate=frecuencia, channels=1, dtype='int16')
    sd.wait()
    print("✅ Procesando y enviando...")

    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(frecuencia)
        wav.writeframes(grabacion.tobytes())
    
    # Enviar el archivo WAV al servidor
    archivos = {'archivo': ('grabacion.wav', buffer.getvalue(), 'audio/wav')}
    respuesta = requests.post(url, files=archivos)
    
    print("\nResultados del servidor:")
    print(respuesta.json())

if __name__ == "__main__":
    grabar_y_enviar()