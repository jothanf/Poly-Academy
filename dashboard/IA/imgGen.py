from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class ImageGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró OPENAI_API_KEY en las variables de entorno")
        self.client = OpenAI(api_key=api_key)

    def generate_image(self, prompt):
        try:
            print(f"Generando imagen para el prompt: {prompt}")
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Retorna la URL de la imagen generada
            return {
                "success": True,
                "url": response.data[0].url
            }
            
        except Exception as e:
            print(f"Error al generar la imagen: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
