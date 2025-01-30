import pytest
from django.test import TestCase, TransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from unittest.mock import patch, MagicMock, AsyncMock
from dashboard.models import ScenarioModel, ClassModel, CourseModel
from chat.consumers import ChatConsumer
from dashboard.IA.openAI import AIService
import json
from asgiref.sync import sync_to_async
from pmback.asgi import application
import asyncio
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from channels.routing import URLRouter
from django.urls import reverse
from asgiref.sync import async_to_sync
from unittest import mock

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

class TestAIService(MagicMock):
    async def chat_with_context_and_check_end(self, *args, **kwargs):
        return "Test response", False

    async def generate_conversation_feedback(self, *args, **kwargs):
        return "Test feedback"

@pytest.mark.asyncio
class ChatConsumerTest:

    @pytest.fixture(autouse=True)
    async def setup(self):
        # Crear un escenario de prueba
        self.class_model = ClassModel.objects.create(
            class_name="Clase de Prueba",
            description="Descripción de la clase de prueba",
            course_id=None  # Asigna una instancia válida de CourseModel si es necesario
        )
        self.scenario = ScenarioModel.objects.create(
            class_id=self.class_model,
            name="Escenario de Prueba",
            description="Descripción del escenario",
            goals="Metas del escenario",
            objectives="Objetivos del escenario",
            student_information="Información del estudiante",
            role_polly="Polly",
            role_student="Estudiante",
            conversation_starter="Hola, ¿cómo estás?",
            end_conversation_saying="Adiós, hasta luego.",
            feedback="Retroalimentación del escenario",
            scoring="Sistema de puntuación",
            additional_info="Información adicional"
        )

        # Mockear AIService para evitar llamadas reales a OpenAI
        self.ai_service_patcher = mock.patch('dashboard.IA.openAI.AIService')
        self.mock_ai_service = self.ai_service_patcher.start()
        self.mock_ai_service_instance = self.mock_ai_service.return_value
        self.mock_ai_service_instance.get_scenario_context.return_value = {
            "role": "system",
            "content": "Contenido de contexto del escenario"
        }
        self.mock_ai_service_instance.get_initial_greeting.return_value = "Hola, ¿cómo puedo ayudarte hoy?"
        self.mock_ai_service_instance.chat_with_context_and_check_end.return_value = ("Respuesta de prueba de la IA", False)
        self.mock_ai_service_instance.generate_conversation_feedback.return_value = "Feedback de prueba"

        yield
        self.ai_service_patcher.stop()

    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_connect_initial_message(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/{self.class_model.class_name}/1/")
        connected, _ = await communicator.connect()
        assert connected

        # Verificar el mensaje inicial
        response = await communicator.receive_json_from()
        assert response['message'] == "Hola, ¿cómo puedo ayudarte hoy?"
        assert response['message_type'] == 'assistant'

        await communicator.disconnect()

    @pytest.mark.django_db
    async def test_connect(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/{self.class_model.class_name}/1/")
        connected, _ = await communicator.connect()
        assert connected

        # Recibir el mensaje inicial
        response = await communicator.receive_json_from()
        assert response['message'] == "Hola, ¿cómo puedo ayudarte hoy?"
        assert response['message_type'] == 'assistant'

        await communicator.disconnect()

    @pytest.mark.django_db
    async def test_disconnect(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/{self.class_model.class_name}/1/")
        connected, _ = await communicator.connect()
        assert connected

        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_end_conversation(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/{self.class_model.class_name}/1/")
        connected, _ = await communicator.connect()
        assert connected

        # Enviar mensaje para finalizar conversación
        end_message = {"message": "fin", "type": "end_conversation"}
        await communicator.send_json_to(end_message)

        # Recibir feedback
        response = await communicator.receive_json_from()
        assert response['message'] == "Feedback de prueba"
        assert response['message_type'] == 'feedback'
        assert response['can_end'] is True

        await communicator.disconnect()
        
    @pytest.mark.django_db
    async def test_send_receive_message(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/{self.class_model.class_name}/1/")
        connected, _ = await communicator.connect()
        assert connected

        # Enviar mensaje
        test_message = {"message": "¿Cuál es la capital de Francia?", "type": "message"}
        await communicator.send_json_to(test_message)

        # Recibir respuesta
        response = await communicator.receive_json_from()
        assert response['message'] == "Respuesta de prueba de la IA"
        assert response['message_type'] == 'assistant'
        assert response['can_end'] is False

        await communicator.disconnect()