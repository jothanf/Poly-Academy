import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from dashboard.IA.openAI import AIService

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

        # Obtener el escenario
        if self.scenario_id:
            self.scenario = await sync_to_async(ScenarioModel.objects.get)(id=self.scenario_id)
            # Asegúrate de que el contexto se esté generando correctamente
            self.conversation_history = [await sync_to_async(self.ai_service.get_scenario_context)(self.scenario)]

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

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

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            print(f"Mensaje recibido del usuario: {message}")

            # Agregar el mensaje del usuario al historial
            self.conversation_history.append({
                'role': 'user',
                'content': message
            })

            # Usar el nuevo método que mantiene el contexto
            response = await sync_to_async(self.ai_service.chat_with_context)(
                message, 
                self.conversation_history,
                self.scenario
            )
            
            print(f"Respuesta de ChatGPT: {response}")

            # Agregar la respuesta del asistente al historial
            self.conversation_history.append({
                'role': 'assistant',
                'content': response
            })

            if response.startswith("Error"):
                print(f"Error detectado: {response}")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': response
                }
            )
        except Exception as e:
            print(f"Error en receive: {str(e)}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f"Error: {str(e)}"
                }
            )

    async def chat_message(self, event):
        message = event['message']
        print(f"Enviando mensaje al WebSocket: {message}")
        await self.send(text_data=json.dumps({
            'message': message
        })) 