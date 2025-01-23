from openAI import AIService

def generate_test_audios():
    # Texto de prueba
    test_text = "Hello! This is a test of the text-to-speech system with different voices."
    # Lista de voces disponibles
    voices = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]
    
    ai_service = AIService()
    
    # Generar un audio para cada voz
    for voice in voices:
        output_file = f"test_audio_{voice}.mp3"
        ai_service.text_to_speech(test_text, voice=voice, output_file=output_file)
       

# Ejecutar la función de prueba
if __name__ == "__main__":
    generate_test_audios()
