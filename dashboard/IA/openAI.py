import os
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import json


load_dotenv()


class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró OPENAI_API_KEY en las variables de entorno")
        print(f"Inicializando AIService con API key: {api_key[:5]}...")  # Solo muestra los primeros 5 caracteres por seguridad
        self.client = OpenAI(api_key=api_key)
        
    def chat_with_gpt(self, user_message):
        try:
            print(f"Enviando mensaje a OpenAI: {user_message}")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500
            )
            response_text = response.choices[0].message.content
            print(f"Respuesta recibida de OpenAI: {response_text[:100]}...")  # Solo muestra los primeros 100 caracteres
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
            # Obtener el nivel del estudiante a partir del CourseModel
            student_level = scenario.class_model.course.level if scenario.class_model and scenario.class_model.course else "Desconocido"

            # Construir el contexto base
            context = {
                "role": "system",
                "content": f"""Eres un asistente de idiomas llamado {scenario.role_polly} en el siguiente contexto:

Escenario: {scenario.name}
Ubicación: {scenario.location}
Descripción: {scenario.description}


Tu rol específico:
- Actúas como: {scenario.role_polly}
- Objetivos de aprendizaje: {json.dumps(scenario.goals, ensure_ascii=False)}
- Vocabulario clave: {json.dumps(scenario.vocabulary, ensure_ascii=False)}
- Expresiones clave: {json.dumps(scenario.key_expressions, ensure_ascii=False)}

Limitaciones y directrices:
{json.dumps(scenario.limitations_polly, ensure_ascii=False)}

Instrucciones específicas:
{json.dumps(scenario.instructions_polly, ensure_ascii=False)}

El estudiante actuará como: {scenario.role_student}
Nivel del estudiante: {student_level}
Limitaciones del estudiante: {scenario.limitations_student}

Mantén la conversación dentro de este contexto y ayuda al estudiante a practicar el idioma de manera natural."""
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
        try:
            context = self.get_scenario_context(scenario)
            
            messages = [
                context,
                {
                    "role": "user",
                    "content": "Por favor, inicia la conversación saludando y presentándote según el contexto del escenario."
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error al generar saludo inicial: {str(e)}")
            return "¡Hola! Bienvenido a nuestra conversación."
