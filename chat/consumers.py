import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from dashboard.IA.openAI import AIService
from django.core.exceptions import ObjectDoesNotExist
import logging
from .models import ConversationHistory
from dashboard.models import ScenarioModel, StudentModel
from channels.db import database_sync_to_async
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_service = AIService()
        self.message_queue = asyncio.Queue()
        self.is_processing = False
        self.conversation_history = []  # Para mantener el historial
        self.scenario = None

    async def connect(self):
        print("\n=== INICIO DE CONEXIÓN WEBSOCKET ===")
        
        # 1. Obtener IDs de la URL
        self.scenario_id = self.scope['url_route']['kwargs']['scenario_id']
        self.student_id = self.scope['url_route']['kwargs']['student_id']
        self.room_name = f"room_{self.scenario_id}_{self.student_id}"
        
        print(f"Datos de conexión:")
        print(f"- Scenario ID: {self.scenario_id}")
        print(f"- Student ID: {self.student_id}")
        print(f"- Room Name: {self.room_name}")
        
        try:
            # 2. Verificar existencia de datos
            print("Verificando existencia de datos...")
            self.scenario = await database_sync_to_async(ScenarioModel.objects.get)(id=self.scenario_id)
            print(f"- Escenario encontrado: {self.scenario.name}")
            
            self.student = await database_sync_to_async(StudentModel.objects.get)(id=self.student_id)
            print(f"- Estudiante encontrado: {self.student.user.username}")
            
            # 3. Inicializar historial
            print("Inicializando historial...")
            history, created = await database_sync_to_async(ConversationHistory.objects.get_or_create)(
                scenario=self.scenario,
                student=self.student,
                defaults={'messages': []}
            )
            print(f"- Historial {'creado' if created else 'recuperado'}")
            
            self.conversation_history = history.messages
            
            # 4. Configurar canal
            print("Configurando canal...")
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            
            # 5. Aceptar conexión
            await self.accept()
            print("Conexión aceptada")
            
            # 6. Enviar mensaje inicial
            await self.send_json({
                'message': self.scenario.conversation_starter,
                'role': 'assistant',
                'message_type': 'message'
            })
            print("Mensaje inicial enviado")
            
        except Exception as e:
            print(f"ERROR en conexión: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            await self.close()
            return False

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_name'):
                await self.channel_layer.group_discard(
                    self.room_name,
                    self.channel_name
                )
        except Exception as e:
            print(f"Error en desconexión: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            message_type = data.get('type', 'message')
            
            print(f"Mensaje recibido en {self.room_name}: {text_data}")

            # Añadir mensaje del usuario al historial
            self.conversation_history.append({
                "role": "user",
                "content": message
            })

            # Procesar con AI
            try:
                ai_service = AIService()
                response = await database_sync_to_async(ai_service.chat_with_gpt)(
                    message,
                    self.conversation_history
                )
                
                # Añadir respuesta al historial
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })

                # Guardar historial actualizado
                await database_sync_to_async(ConversationHistory.objects.filter(
                    scenario=self.scenario,
                    student=self.student
                ).update)(messages=self.conversation_history)

                print(f"Respuesta AI para {self.room_name}: {response}")

            except Exception as e:
                print(f"Error al comunicarse con OpenAI: {str(e)}")
                response = "Lo siento, hubo un error procesando tu mensaje."

            # Enviar respuesta al grupo
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': response,
                    'role': 'assistant',
                    'message_type': message_type
                }
            )

        except Exception as e:
            print(f"Error en receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'message': "Error procesando el mensaje",
                'role': 'assistant',
                'message_type': 'error'
            }))

    async def chat_message(self, event):
        # Enviar mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'role': event.get('role', 'assistant'),
            'message_type': event.get('message_type', 'message')
        })) 