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

# Ejemplos de uso con diferentes configuraciones
texto = "Hola, soy POLLY tu asistente virtual. Estoy aquí para ayudarte a mejorar tus habilidades en este idioma. ¡Vamos a aprender juntos!"

texto_ingles = "Hello, I am POLLY your virtual assistant. I am here to help you improve your skills in this language. Let's learn together!"



# Configuraciones de prueba
configuraciones = [
    {
        "voz": "es-ES-Studio-F",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_es_es_studio_F_vel_1.1_tono_-2.0"
    },
    {
        "voz": "es-ES-Standard-F",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_es_es_standard_F_vel_1.1_tono_-2.0"
    },
    {
        "voz": "es-ES-Studio-C",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_es_es_studio_C_vel_1.1_tono_-2.0"
    },
    {
        "voz": "es-ES-Standard-A",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_es_es_standard_A_vel_1.1_tono_-2.0"
    },
    {
        "voz": "es-ES-Standard-B",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_es_es_standard_B_vel_1.1_tono_-2.0"
    },
    {
        "voz": "es-US-Standard-A",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_es_us_standard_A_vel_1.1_tono_-2.0"
    },
    {
        "voz": "es-US-Standard-B",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_es_us_standard_B_vel_1.1_tono_-2.0"
    },
    {
        "voz": "es-US-Standard-C",
        "velocidad": 1.1,
        "tono": -1.0,
        "nombre": "masculino_es_us_standard_C_vel_1.1_tono_-1.0"
    },
    {
        "voz": "es-US-Standard-C",
        "velocidad": 1.3,
        "tono": -1.0,
        "nombre": "masculino_es_us_standard_C_vel_1.3_tono_-1.0"
    },
    {
        "voz": "es-US-Standard-C",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_es_us_standard_C_vel_1.1_tono_-2.0"
    },
    {
        "voz": "es-US-Standard-C",
        "velocidad": 1.3,
        "tono": -2.0,
        "nombre": "masculino_es_us_standard_C_vel_1.3_tono_-2.0"
    },
    {
        "voz": "es-US-Standard-C",
        "velocidad": 1.1,
        "tono": -3.0,
        "nombre": "masculino_es_us_standard_C_vel_1.1_tono_-3.0"
    },
    {
        "voz": "es-US-Standard-C",
        "velocidad": 1.3,
        "tono": -3.0,
        "nombre": "masculino_es_us_standard_C_vel_1.3_tono_-3.0"
    },
    {
        "voz": "en-AU-Standard-A",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_en_au_standard_A_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-AU-Standard-B",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_en_au_standard_B_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-AU-Standard-C",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_en_au_standard_C_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-AU-Standard-D",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_en_au_standard_D_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-GB-Standard-A",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_en_gb_standard_A_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-GB-Standard-B",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_en_gb_standard_B_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-GB-Standard-C",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_en_gb_standard_C_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-GB-Standard-D",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_en_gb_standard_D_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-US-Standard-A",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_en_us_standard_A_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-US-Standard-B",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "masculino_en_us_standard_B_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-US-Standard-C",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_en_us_standard_C_vel_1.1_tono_-2.0"
    },
    {
        "voz": "en-US-Standard-F",
        "velocidad": 1.1,
        "tono": -2.0,
        "nombre": "femenino_en_us_standard_F_vel_1.1_tono_-2.0"
    }
]

# Textos para diferentes idiomas
texto_espanol = "Hola, soy POLLY tu asistente virtual. Estoy aquí para ayudarte a mejorar tus habilidades en este idioma. ¡Vamos a aprender juntos!"
texto_ingles = "Hello, I am POLLY your virtual assistant. I am here to help you improve your skills in this language. Let's learn together!"

# Genera los audios de prueba
for config in configuraciones:
    ruta_audio = f"salidas/{config['nombre']}.mp3"
    
    # Determina el idioma y el texto basado en la voz
    if config['voz'].startswith('es-'):
        texto_usar = texto_espanol
        idioma = "es-ES"
    else:  # voces en inglés
        texto_usar = texto_ingles
        idioma = config['voz'][:5]  # Toma los primeros 5 caracteres (ej: "en-US", "en-GB")
    
    texto_a_audio_google(
        texto=texto_usar,
        ruta_salida=ruta_audio,
        idioma=idioma,
        voz=config["voz"],
        velocidad=config["velocidad"],
        tono=config["tono"]
    )
