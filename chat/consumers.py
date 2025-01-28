import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from dashboard.IA.openAI import AIService
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_service = AIService()
        self.conversation_history = []  # Para mantener el historial
        self.scenario = None

    async def connect(self):
        from dashboard.models import ScenarioModel
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.scenario_id = self.scope['url_route']['kwargs'].get('scenario_id')
        self.room_group_name = f'chat_{self.room_name}'
        
        logger.debug(f"Intentando conectar a la sala: {self.room_group_name} con escenario: {self.scenario_id}")

        # Validar el scenario_id
        if self.scenario_id and self.scenario_id.isdigit():
            try:
                self.scenario = await sync_to_async(ScenarioModel.objects.get)(id=self.scenario_id)
                print(f"Escenario obtenido: {self.scenario.name}")
            # Asegúrate de que el contexto se esté generando correctamente
                self.conversation_history = [await sync_to_async(self.ai_service.get_scenario_context)(self.scenario)]
            except ObjectDoesNotExist:
                # Si el escenario no existe, cerrar la conexión
                await self.close()
                return
        else:
            # Si el scenario_id no es válido, cerrar la conexión
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Conexión aceptada para la sala: {self.room_group_name}")

        # Agregar este nuevo código para iniciar la conversación
        if self.scenario:
            initial_message = await sync_to_async(self.ai_service.get_initial_greeting)(self.scenario)
            
            # Agregar el mensaje inicial al historial
            self.conversation_history.append({
                'role': 'assistant',
                'content': initial_message
            })

            # Enviar el mensaje inicial
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': initial_message
                }
            )

    async def disconnect(self, close_code):
        # Abandonar el grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Desconexión de la sala: {self.room_group_name}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'end_conversation':
                feedback = await sync_to_async(self.ai_service.generate_conversation_feedback)(
                    self.conversation_history,
                    self.scenario
                )
                print(f"Conversación finalizada. Enviando feedback: {feedback}")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': feedback,
                        'message_type': 'feedback',
                        'can_end': True
                    }
                )
                return

            # Agregar el mensaje del usuario al historial
            self.conversation_history.append({
                'role': 'user',
                'content': message
            })

            # Obtener respuesta y análisis de finalización
            response, can_end = await sync_to_async(self.ai_service.chat_with_context_and_check_end)(
                message, 
                self.conversation_history, 
                self.scenario
            )
            
            print(f"Respuesta generada. Can end: {can_end}")
            
            # Agregar la respuesta del asistente al historial
            self.conversation_history.append({
                'role': 'assistant',
                'content': response
            })
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': response,
                    'can_end': can_end,
                    'message_type': 'assistant'
                }
            )
            print(f"Mensaje enviado al grupo: {response}")

        except Exception as e:
            print(f"Error en receive: {str(e)}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f"Error: {str(e)}",
                    'can_end': False
                }
            )

    async def chat_message(self, event):
        message = event['message']
        can_end = event.get('can_end', False)
        message_type = event.get('message_type', 'message')
        
        print(f"Enviando mensaje al WebSocket: {message}")
        print(f"Estado can_end: {can_end}")
        
        await self.send(text_data=json.dumps({
            'message': message,
            'can_end': can_end,
            'message_type': message_type
        })) 