import librosa
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import joblib
import os

def extraer_mfcc(ruta_audio):
    # Cargar audio a 16kHz y extraer 13 coeficientes MFCC
    y, sr = librosa.load(ruta_audio, sr=16000)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

X = []
y = []
ruta_dataset = "dataset_voces"

#  los 3 usuarios válidos del equipo
usuarios_esperados = ["aaron", "aide", "luis"]

if not os.path.exists(ruta_dataset):
    print(f"Error: No se encontró la carpeta '{ruta_dataset}'.")
    exit()

print("Procesando audios para el equipo: Aarón, Aidé y Luis...")

for nombre_persona in os.listdir(ruta_dataset):
    nombre_normalizado = nombre_persona.lower()
    
    # Ignorar cualquier carpeta que no pertenezca
    if nombre_normalizado not in usuarios_esperados:
        continue
        
    ruta_persona = os.path.join(ruta_dataset, nombre_persona)
    
    if os.path.isdir(ruta_persona):
        for archivo in os.listdir(ruta_persona):
            if archivo.endswith(".wav"):
                ruta_completa = os.path.join(ruta_persona, archivo)
                try:
                    caracteristicas = extraer_mfcc(ruta_completa)
                    X.append(caracteristicas)
                    y.append(nombre_normalizado) 
                    print(f"  -> Procesado: {archivo} (Usuario: {nombre_normalizado})")
                except Exception as e:
                    print(f"  -> Error al leer {archivo}: {e}")

if len(X) == 0:
    print("Error: No se encontraron archivos .wav válidos en las carpetas de aaron, aide o luis.")
    exit()

X = np.array(X)

print("\nEntrenando modelo K-NN para 3 clases...")
# n_neighbors=1 asocia la voz nueva a la muestra más cercana
knn = KNeighborsClassifier(n_neighbors=1) 
knn.fit(X, y)

os.makedirs("modelos", exist_ok=True)
joblib.dump(knn, "modelos/clasificador_voz.pkl")
print(f"\n¡Modelo entrenado con {len(X)} muestras y guardado exitosamente!")