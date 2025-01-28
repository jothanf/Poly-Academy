import os
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import json
import logging


load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró OPENAI_API_KEY en las variables de entorno")
        print(f"Inicializando AIService con API key: {api_key[:5]}...")  # Solo muestra los primeros 5 caracteres por seguridad
        self.client = OpenAI(api_key=api_key)
        
    def chat_with_gpt(self, user_message, conversation_history=None):
        logger.debug(f"Chat con GPT iniciado con mensaje: {user_message}")
        try:
            if conversation_history is None:
                conversation_history = []
            
            # Si no hay historial, agregar el system prompt
            if not conversation_history:
                conversation_history.append({
                    "role": "system",
                    "content": """Eres POLLY, una profesora de inglés carismática y experta..."""
                })
            
            print(f"Enviando mensaje a OpenAI: {user_message}")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=conversation_history,
                max_tokens=500,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            print(f"Respuesta recibida de OpenAI: {response_text[:100]}...")
            return response_text
        except Exception as e:
            error_message = f"Error al comunicarse con OpenAI: {str(e)}"
            print(error_message)
            return error_message
    
    def analyze_pronunciation(self, transcription, original_text=None):
        try:
            print(f"Analizando transcripción: {transcription}")
            
            # Modificamos el prompt para ser más específico
            prompt = f"""You are a language teacher. Analyze the following English transcription:
            "{transcription}"
            
            Provide a brief analysis focusing on:
            1. Overall pronunciation quality
            2. Specific areas for improvement
            3. A score from 1 to 10

            IMPORTANT: Your response must be in valid JSON format with this exact structure:
            {{
                "feedback": "overall feedback about the pronunciation",
                "improvements": ["improvement area 1", "improvement area 2"],
                "score": number
            }}

            RESPOND ONLY WITH THE JSON, NO ADDITIONAL TEXT."""

            print(f"Enviando prompt a GPT: {prompt}")

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a language teacher that provides pronunciation feedback in JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"Respuesta de GPT: {response_text}")
            
            # Verificar que la respuesta sea JSON válido
            try:
                # Intentar parsear para validar
                json_response = json.loads(response_text)
                # Asegurar que tiene la estructura correcta
                if not all(key in json_response for key in ['feedback', 'improvements', 'score']):
                    raise ValueError("Respuesta JSON incompleta")
                return response_text
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error al validar JSON: {e}")
                # Crear una respuesta JSON válida en caso de error
                return json.dumps({
                    "feedback": "El análisis no pudo ser procesado correctamente. Por favor, intenta de nuevo.",
                    "improvements": ["Intenta hablar más claro", "Asegúrate de estar en un ambiente silencioso"],
                    "score": 5
                })

        except Exception as e:
            print(f"Error en analyze_pronunciation: {str(e)}")
            return json.dumps({
                "feedback": "Error en el análisis de pronunciación. Por favor, intenta de nuevo.",
                "improvements": [],
                "score": 0
            })

    def transcribe_audio(self, audio_file):
        try:
            print("Iniciando transcripción de audio")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()
                
                print(f"Archivo temporal creado: {temp_file.name}")
                
                with open(temp_file.name, 'rb') as audio:
                    print("Enviando audio a Whisper")
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        response_format="text"
                    )
                    print(f"Transcripción recibida: {transcript}")

            os.unlink(temp_file.name)
            print("Archivo temporal eliminado")
            
            print("Iniciando análisis de pronunciación")
            pronunciation_analysis = self.analyze_pronunciation(transcript)
            print(f"Análisis de pronunciación completado: {pronunciation_analysis}")
            
            return {
                "transcription": transcript,
                "pronunciation_analysis": pronunciation_analysis
            }
        except Exception as e:
            print(f"Error detallado en transcribe_audio: {str(e)}")
            return f"Error al procesar el audio: {str(e)}"

    def generate_scenario_suggestions(self, scenario_info):
        try:
            prompt = f"""Based on this English practice scenario information:
            - Name: {scenario_info.get('nombre', '')}
            - Level: {scenario_info.get('nivel', '')}
            - Type: {scenario_info.get('tipo', '')}
            - Location: {scenario_info.get('lugar', '')}
            - Description: {scenario_info.get('descripcion', '')}

            Please suggest appropriate content for:
            1. AI Character role and characteristics
            2. Student role and context
            3. Grammar structures and semantic fields
            4. Useful expressions

            Provide the response in a clean JSON format without markdown formatting."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a language teaching expert. Provide suggestions in clean JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Limpiar la respuesta de cualquier formato markdown
            response_text = response.choices[0].message.content.strip()
            # Eliminar cualquier bloque de código markdown si existe
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "")
            
            # Asegurarse de que es JSON válido
            return json.loads(response_text)
        except Exception as e:
            print(f"Error en generate_scenario_suggestions: {str(e)}")
            return {
                "error": "No se pudieron generar sugerencias",
                "details": str(e)
            }

    def get_scenario_context(self, scenario):
        """
        Genera el contexto del escenario para OpenAI basado en el modelo ScenarioModel
        """
        try:
            # Obtener el nivel del estudiante
            student_level = scenario.class_id.course.level if scenario.class_id and scenario.class_id.course else "Desconocido"

            context = {
                "role": "system",
                "content": f"""Eres un asistente de idiomas con las siguientes características específicas:

IDENTIDAD Y ROL:
- Tu nombre/rol es: {scenario.role_polly}
- Debes mantener este rol consistentemente durante toda la conversación
- Siempre inicia la conversación exactamente con: "{scenario.conversation_starter}"
- Debes terminar la conversación con: "{scenario.end_conversation_saying}"

OBJETIVOS DE LA CONVERSACIÓN:
- Metas principales: {scenario.goals}
- Objetivos específicos: {scenario.objectives}

CONTEXTO DEL ESTUDIANTE:
- El estudiante actúa como: {scenario.role_student}
- Nivel del estudiante: {student_level}
- Información relevante del estudiante: {scenario.student_information}

CONTENIDO LINGÜÍSTICO:
- Vocabulario a enfatizar: {scenario.vocabulary}
- Expresiones clave a utilizar: {scenario.key_expressions}

DIRECTRICES DE INTERACCIÓN:
- Descripción del escenario: {scenario.description}
- Criterios para terminar la conversación: {scenario.end_conversation}
- Retroalimentación: {scenario.feedback}
- Sistema de puntuación: {scenario.scoring}

REGLAS ESTRICTAS:
1. SIEMPRE inicia con el saludo exacto especificado
2. Mantén el rol y personalidad consistentes
3. Utiliza el vocabulario y expresiones especificadas
4. Proporciona retroalimentación según los criterios establecidos
5. Termina la conversación solo bajo las condiciones especificadas
6. Usa el cierre de conversación exacto cuando sea apropiado

Información adicional: {scenario.additional_info}"""
            }
            
            return context
        except Exception as e:
            print(f"Error generando contexto del escenario: {str(e)}")
            return {
                "role": "system",
                "content": "Error al cargar el contexto del escenario. Por favor, utiliza un contexto de conversación básico."
            }

    def chat_with_context(self, user_message, conversation_history, scenario):
        try:
            # Si no hay historial, inicializar con el contexto del escenario
            if not conversation_history:
                conversation_history = [self.get_scenario_context(scenario)]
            
            # Añadir el mensaje del usuario al historial
            conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Limitar el historial a las últimas 10 interacciones para evitar tokens excesivos
            if len(conversation_history) > 10:
                # Mantener siempre el contexto inicial y los últimos mensajes
                conversation_history = [conversation_history[0]] + conversation_history[-9:]

            response = self.client.chat.completions.create(
                model="gpt-4",  # Asegúrate de usar el modelo correcto
                messages=conversation_history,
                max_tokens=500
            )

            assistant_response = response.choices[0].message.content
            
            # Añadir la respuesta del asistente al historial
            conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })

            return assistant_response
        except Exception as e:
            error_message = f"Error al comunicarse con OpenAI: {str(e)}"
            print(error_message)
            return error_message

    def get_initial_greeting(self, scenario):
        """
        Retorna el saludo inicial exacto especificado en el escenario
        """
        try:
            return scenario.conversation_starter
        except Exception as e:
            print(f"Error al generar saludo inicial: {str(e)}")
            return "¡Hola! Bienvenido a nuestra conversación."

    def text_to_speech(self, text, voice="alloy", output_file="output.mp3"):
        try:
            print(f"Generando audio a partir del texto: {text}")
            allowed_voices = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]
            if voice not in allowed_voices:
                raise ValueError(f"Voz no válida. Debe ser una de las siguientes: {', '.join(allowed_voices)}")
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )
            
            # Escribir el contenido del audio directamente al archivo
            with open(output_file, 'wb') as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
                
            print(f"Audio generado y guardado en: {output_file}")
            return output_file
        except Exception as e:
            print(f"Error al generar audio: {str(e)}")
            return None

    def chat_with_context_and_check_end(self, user_message, conversation_history, scenario):
        """
        Versión modificada de chat_with_context que también analiza si la conversación puede terminar
        """
        try:
            # Obtener la respuesta normal
            response = self.chat_with_context(user_message, conversation_history, scenario)
            
            # Analizar si se cumplen las condiciones de finalización
            analysis_prompt = f"""
            Basado en los siguientes criterios de finalización:
            {scenario.end_conversation}
            
            Y considerando esta conversación:
            {conversation_history}
            
            ¿Se han cumplido las condiciones para finalizar la conversación?
            Responde solo con 'true' o 'false'.
            """
            
            can_end_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=10,
                temperature=0
            )
            
            can_end = can_end_response.choices[0].message.content.strip().lower() == 'true'
            
            return response, can_end
            
        except Exception as e:
            print(f"Error en chat_with_context_and_check_end: {str(e)}")
            return str(e), False
            
    def generate_conversation_feedback(self, conversation_history, scenario):
        """
        Genera retroalimentación final de la conversación
        """
        try:
            feedback_prompt = f"""
            Basado en los siguientes criterios de retroalimentación:
            {scenario.feedback}
            
            Y sistema de puntuación:
            {scenario.scoring}
            
            Analiza esta conversación:
            {conversation_history}
            
            Proporciona:
            1. Una evaluación detallada
            2. Puntos fuertes
            3. Áreas de mejora
            4. Puntuación según los criterios establecidos
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": feedback_prompt}],
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generando retroalimentación: {str(e)}"

