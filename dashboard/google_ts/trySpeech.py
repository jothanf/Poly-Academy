"""from google.cloud import speech
import io
from gtts import gTTS  # Importa la biblioteca gTTS
import os  # Importa os para manejar archivos

def texto_a_audio(texto, ruta_salida):
    # Convierte el texto a audio
    tts = gTTS(text=texto, lang='es')  # Especifica el idioma
    # Asegúrate de que el directorio de salida exista
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)  # Crea el directorio si no existe
    tts.save(ruta_salida)  # Guarda el archivo de audio

# Ejemplo de uso de la nueva función
texto = "Hola, soy sofia y me gusta comer mocos"
ruta_audio = "ruta/al/audio_salida.mp3"
texto_a_audio(texto, ruta_audio)  # Llama a la función para convertir texto a audio
"""

from google.cloud import texttospeech
import os

# Define la ruta al archivo de credenciales
ruta_credenciales = os.path.join(os.path.dirname(__file__), '../../ardent-course-446319-k0-078e381fd893.json')  # Ajusta la ruta según sea necesario

# Establece las credenciales de Google
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ruta_credenciales

def texto_a_audio_google(texto, ruta_salida, idioma="es-ES", voz="es-ES-Wavenet-A", velocidad=1.0, tono=0.0):
    # Inicializa el cliente de Text-to-Speech
    client = texttospeech.TextToSpeechClient()

    # Configura el texto a convertir
    input_text = texttospeech.SynthesisInput(text=texto)

    # Configura la voz: idioma, género y tipo
    voice = texttospeech.VoiceSelectionParams(
        language_code=idioma,  # Idioma (ej. "es-ES" para español)
        name=voz  # Voz específica (ej. "es-ES-Wavenet-A")
    )

    # Configura los parámetros de audio: velocidad, tono, etc.
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,  # Formato del audio
        speaking_rate=velocidad,  # Velocidad (1.0 es normal, 0.5 es más lento, 2.0 es más rápido)
        pitch=tono  # Tono (-20.0 para más grave, +20.0 para más agudo)
    )

    # Genera el audio
    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config
    )

    # Guarda el audio en la ruta especificada
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)  # Crea el directorio si no existe
    with open(ruta_salida, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio guardado en: {ruta_salida}")

# Ejemplo de uso
texto = "Hola, esta es una prueba de conversión de texto a audio con Google Text-to-Speech."
ruta_audio = "salidas/audio_google.mp3"
texto_a_audio_google(texto, ruta_audio, idioma="es-ES", voz="es-ES-Wavenet-B", velocidad=1.2, tono=-5.0)
