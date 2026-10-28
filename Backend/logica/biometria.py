import joblib
import librosa
import numpy as np
import io
import os

# Ruta al modelo entrenado
ruta_modelo = os.path.join("modelos", "clasificador_voz.pkl")

# Cargar el modelo a la memoria al iniciar este módulo
try:
    modelo_knn = joblib.load(ruta_modelo)
    print("Modelo biométrico cargado correctamente en memoria.")
except Exception as e:
    print(f"Error al cargar el modelo: {e}. Asegúrate de haber ejecutado entrenar_modelo.py")
    modelo_knn = None

def identificar_usuario(bytes_audio):
    if modelo_knn is None:
        return "Error: Modelo no cargado"

    try:
        # Convertir los datos formato que librosa pueda procesar
        archivo_audio = io.BytesIO(bytes_audio)
        y, sr = librosa.load(archivo_audio, sr=16000)
        
        # Extraer características 
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        vector_caracteristicas = np.mean(mfcc.T, axis=0).reshape(1, -1)
        
        # Predecir a quién pertenece la voz
        prediccion = modelo_knn.predict(vector_caracteristicas)
        return prediccion[0]  # Retornará "aaron", "aide" o "luis"
        
    except Exception as e:
        print(f"Error procesando el audio entrante: {e}")
        return "desconocido"