import pytest
from django.test import TestCase, TransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from unittest.mock import patch, MagicMock
from dashboard.models import ScenarioModel, ClassModel, CourseModel
from chat.consumers import ChatConsumer
from dashboard.IA.openAI import AIService
import json
from asgiref.sync import sync_to_async
from pmback.asgi import application
import asyncio

pytestmark = pytest.mark.asyncio

class AIServiceChatTest(TestCase):
    def setUp(self):
        # Crear curso y clase necesarios para el escenario
        self.course = CourseModel.objects.create(
            course_name="Test Course",
            description="Test Description"
        )
        self.class_model = ClassModel.objects.create(
            class_name="Test Class",
            course=self.course
        )
        
        # Crear escenario de prueba
        self.scenario = ScenarioModel.objects.create(
            class_id=self.class_model,
            name="Test Scenario",
            role_polly="English Teacher",
            role_student="Student",
            conversation_starter="Hello! Welcome to the class.",
            end_conversation="The student has completed all required tasks.",
            end_conversation_saying="Thank you for the class!",
            feedback="Evaluate grammar and vocabulary usage.",
            scoring="Score based on correct responses."
        )
        
        self.ai_service = AIService()
        self.conversation_history = []

    @patch('openai.ChatCompletion.create')
    def test_chat_with_context_and_check_end(self, mock_create):
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_create.return_value = mock_response

        # Probar la función
        response, can_end = self.ai_service.chat_with_context_and_check_end(
            "Hello teacher", 
            self.conversation_history, 
            self.scenario
        )
        
        self.assertIsNotNone(response)
        self.assertIsInstance(can_end, bool)

    def test_get_scenario_context(self):
        context = self.ai_service.get_scenario_context(self.scenario)
        
        self.assertIsInstance(context, dict)
        self.assertEqual(context['role'], 'system')
        self.assertIn(self.scenario.role_polly, context['content'])
        self.assertIn(self.scenario.conversation_starter, context['content'])

    @patch('openai.ChatCompletion.create')
    def test_generate_conversation_feedback(self, mock_create):
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test feedback"
        mock_create.return_value = mock_response

        feedback = self.ai_service.generate_conversation_feedback(
            self.conversation_history,
            self.scenario
        )
        
        self.assertIsNotNone(feedback)
        self.assertIsInstance(feedback, str)

class ChatConsumerTest(TransactionTestCase):
    async def asyncSetUp(self):
        # Crear una clase para asociar con el escenario
        self.class_model = await sync_to_async(ClassModel.objects.create)(
            class_name='Clase de Prueba',
            description='Descripción de la clase de prueba',
            course_id=None  # Asignar si es necesario
        )
        
        # Crear un escenario para las pruebas
        self.scenario = await sync_to_async(ScenarioModel.objects.create)(
            class_id=self.class_model,
            name='Escenario de Prueba',
            description='Descripción del escenario de prueba',
            goals='Metas del escenario',
            objectives='Objetivos del escenario',
            student_information='Información del estudiante',
            role_polly='Profesor',
            role_student='Estudiante',
            conversation_starter='¡Hola! ¿Cómo estás?',
            end_conversation='La conversación termina cuando se complete el objetivo',
            end_conversation_saying='¡Gracias por la conversación!',
            feedback='Feedback del escenario',
            scoring='Criterios de puntuación'
        )
        
        # Inicializar el comunicador de WebSocket
        self.communicator = WebsocketCommunicator(
            application=application,
            path=f"/ws/chat/test/?scenario_id={self.scenario.id}"
        )
        connected, subprotocol = await self.communicator.connect()
        self.assertTrue(connected)
        print(f"Escenario creado: {self.scenario.id} - {self.scenario.name}")

    async def asyncTearDown(self):
        await self.communicator.disconnect()
        print("Desconexión completada.")

    @patch('chat.consumers.AIService')
    async def test_connect(self, mock_ai_service):
        print("Iniciando prueba de conexión...")
        # La conexión ya se realiza en asyncSetUp
        pass

    @patch('chat.consumers.AIService')
    async def test_disconnect(self, mock_ai_service):
        print("Iniciando prueba de desconexión...")
        await self.communicator.disconnect()
        # Intentar desconectar nuevamente no debe causar errores
        pass

    @patch('chat.consumers.AIService')
    async def test_receive_message(self, mock_ai_service):
        print("Iniciando prueba de envío y recepción de mensajes...")
        # Configurar el mock de AIService
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta de prueba"
        mock_ai_service().chat_with_context_and_check_end.return_value = ("Respuesta de prueba", False)
        
        # Enviar un mensaje de prueba
        await self.communicator.send_json_to({
            "message": "Hola, ¿cómo estás?"
        })
        
        # Recibir la respuesta
        response = await self.communicator.receive_json_from()
        self.assertIn('message', response)
        self.assertEqual(response['message'], "Respuesta de prueba")
        print(f"Mensaje recibido: {response['message']}")

    @patch('chat.consumers.AIService')
    async def test_end_conversation(self, mock_ai_service):
        print("Iniciando prueba de fin de conversación...")
        # Configurar el mock de AIService
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Conversación terminada."
        mock_ai_service().chat_with_context_and_check_end.return_value = ("Conversación terminada.", True)
        
        # Enviar un mensaje para terminar la conversación
        await self.communicator.send_json_to({
            "message": "Gracias, adiós",
            "type": "end_conversation"
        })
        
        # Recibir la respuesta
        response = await self.communicator.receive_json_from()
        self.assertIn('message', response)
        self.assertEqual(response['message_type'], 'feedback')
        self.assertTrue(response['can_end'])
        print(f"Feedback recibido: {response['message']}")