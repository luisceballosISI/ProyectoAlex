# logica/audio_utils.py
import speech_recognition as sr
from gtts import gTTS
import io

def transcribir_audio(wav_bytes):
    r = sr.Recognizer()
    try:
        # Convertir los bytes en un archivo de audio en memoria
        with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
            audio = r.record(source)
        # Transcribir usando Google (requiere internet)
        texto = r.recognize_google(audio, language="es-MX")
        return texto
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print(f"Error STT: {e}")
        return ""

def texto_a_audio(texto):
    # Generar voz en español de México
    tts = gTTS(text=texto, lang='es', tld='com.mx')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue() # Retorna los bytes del archivo MP3s