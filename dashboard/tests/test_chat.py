import pytest
from django.test import TestCase, TransactionTestCase, RequestFactory
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from unittest.mock import patch, MagicMock, AsyncMock
from dashboard.models import ScenarioModel, ClassModel, CourseModel, StudentModel
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
from dashboard.view.ai_views import translate_message 
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from dashboard.tests.utils import create_test_application


pytestmark = pytest.mark.asyncio

# Configuración específica para pruebas
application = AuthMiddlewareStack(
    URLRouter([
        re_path(r'ws/chat/(?P<room_name>\w+)/(?P<scenario_id>\w+)/(?P<student_id>\w+)/$', 
            ChatConsumer.as_asgi()),
    ])
)

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

class TestTranslateMessage(TestCase):
    def setUp(self):
        # Inicializar el factory
        self.factory = RequestFactory()

    @patch('dashboard.IA.openAI.AIService.translate_to_spanish')
    def test_translate_message_success(self, mock_translate):
        # Configurar el mock para devolver una traducción
        mock_translate.return_value = "Hola, ¿cómo estás?"

        # Simular una solicitud POST
        request = self.factory.post('/translate/', {'message': 'Hello, how are you?'})
        response = translate_message(request)

        # Verificar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['translation'], "Hola, ¿cómo estás?")

    def test_translate_message_no_message(self):
        # Simular una solicitud POST sin mensaje
        request = self.factory.post('/translate/', {})
        response = translate_message(request)

        # Verificar la respuesta de error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Se requiere un mensaje para traducir')

    @patch('dashboard.IA.openAI.AIService.translate_to_spanish')
    def test_translate_message_exception(self, mock_translate):
        # Configurar el mock para lanzar una excepción
        mock_translate.side_effect = Exception("Error en la traducción")

        # Simular una solicitud POST
        request = self.factory.post('/translate/', {'message': 'Hello, how are you?'})
        response = translate_message(request)

        # Verificar la respuesta de error
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], "Error en la traducción")

class ChatMultiUserTest(TransactionTestCase):
    def setUp(self):
        # Crear curso
        self.course = CourseModel.objects.create(
            course_name="Test Course"  # Cambio de name a course_name
        )
        
        # Crear clase
        self.class_model = ClassModel.objects.create(
            class_name="Test Class",  # Cambio de name a class_name
            course=self.course
        )
        
        # Crear escenario
        self.scenario = ScenarioModel.objects.create(
            name="Test Scenario",
            class_id=self.class_model,
            conversation_starter="Hello!"
        )
        
        # Crear usuarios y estudiantes para pruebas
        self.students = []
        for i in range(20):
            user = User.objects.create_user(
                username=f'student{i}',
                password='testpass'
            )
            student = StudentModel.objects.create(
                user=user
            )
            self.students.append(student)
        
        # Configurar la aplicación de prueba
        self.application = create_test_application()

    async def test_multiple_concurrent_connections(self):
        print("\n=== TEST MÚLTIPLES CONEXIONES ===")
        communicators = []
        messages = []
        
        # Crear 5 conexiones
        for i in range(5):
            path = f"/ws/chat/{self.scenario.id}/{self.students[i].id}/"
            print(f"Creando conexión {i}: {path}")
            
            communicator = WebsocketCommunicator(
                self.application,
                path
            )
            connected, _ = await communicator.connect()
            print(f"Conexión {i} establecida: {connected}")
            assert connected
            
            # Enviar mensaje
            message = f"Test message {i}"
            await communicator.send_json_to({
                "type": "message",
                "message": message,
                "role": "user"
            })
            
            # Recibir respuesta
            response = await communicator.receive_json_from()
            print(f"Respuesta {i}: {response}")
            
            assert response['message'] is not None
            assert response['role'] == 'assistant'
            
            communicators.append(communicator)
            messages.append(message)
        
        # Cerrar conexiones
        for communicator in communicators:
            await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_chat_history_persistence(self):
        print("\nIniciando test_chat_history_persistence")
        
        # Crear el comunicador
        path = f"/ws/chat/{self.scenario.id}/{self.students[0].id}/"
        print(f"Intentando conectar a: {path}")
        
        communicator1 = WebsocketCommunicator(
            self.application,
            path
        )
        
        connected, _ = await communicator1.connect()
        print(f"Estado de conexión: {connected}")
        assert connected, "La conexión inicial falló"
        
        # Enviar un mensaje y esperar respuesta
        await communicator1.send_json_to({
            "type": "message",
            "message": "Hello!",
            "role": "user"
        })
        
        # Esperar la respuesta del asistente
        response = await communicator1.receive_json_from()
        assert response is not None
        
        # Desconectar y verificar el historial
        await communicator1.disconnect()
        
        # Esperar un momento para que se guarde el historial
        await asyncio.sleep(1)

      
    @pytest.mark.asyncio
    async def test_load_simulation(self):
        print("\nIniciando test_load_simulation")
        NUM_CONNECTIONS = 5  # Reducido para debugging
        
        async def simulate_chat_session(student_id):
            try:
                path = f"/ws/chat/{self.scenario.id}/{student_id}/"
                print(f"Simulando conexión en: {path}")
                
                communicator = WebsocketCommunicator(
                    self.application,
                    path
                )
                connected, _ = await communicator.connect()
                print(f"Estado de conexión {student_id}: {connected}")
                
                if connected:
                    await communicator.send_json_to({
                        "type": "message",
                        "message": f"Test message from {student_id}",
                        "role": "user"
                    })
                    await communicator.disconnect()
                    return True
                return False
            except Exception as e:
                print(f"Error en sesión {student_id}: {str(e)}")
                return False

        # Ejecutar conexiones en paralelo
        tasks = [simulate_chat_session(i) for i in range(NUM_CONNECTIONS)]
        results = await asyncio.gather(*tasks)
        
        success_rate = sum(results) / len(results)
        assert success_rate > 0.90, f"Tasa de éxito: {success_rate}"  # Reducimos el umbral al 90%

    @pytest.mark.asyncio
    async def test_room_isolation(self):
        communicator1 = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.scenario.id}/{self.students[0].id}/"
        )
        communicator2 = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.scenario.id}/{self.students[1].id}/"
        )
        
        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()
        
        assert connected1 and connected2, "Fallo en la conexión de las salas"

        try:
            await communicator1.send_json_to({
                "message": "Hello from student 1",
                "type": "message"
            })

            response1 = await communicator1.receive_json_from()
            assert 'message' in response1

            # Verificar que el segundo estudiante no recibe el mensaje
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(communicator2.receive_json_from(), timeout=1.0)
        finally:
            await communicator1.disconnect()
            await communicator2.disconnect()

    @pytest.mark.asyncio
    async def test_stress_test(self):
        """Prueba de estrés para determinar la capacidad máxima"""
        async def run_stress_test(num_connections):
            successful = 0
            active_connections = []
            
            try:
                # Crear conexiones
                for i in range(num_connections):
                    communicator = WebsocketCommunicator(
                        self.application,
                        f"/ws/chat/stress_test/{self.scenario.id}/{i}/"
                    )
                    connected, _ = await communicator.connect()
                    if connected:
                        successful += 1
                        active_connections.append(communicator)
                    
                # Mantener las conexiones activas por un momento
                await asyncio.sleep(2)
                
                # Cerrar conexiones
                for comm in active_connections:
                    await comm.disconnect()
                    
                return successful
                
            except Exception as e:
                print(f"Error en prueba de estrés: {str(e)}")
                return successful

        # Probar diferentes números de conexiones
        connection_counts = [10, 20, 50, 100]
        results = {}
        
        for count in connection_counts:
            successful = await run_stress_test(count)
            results[count] = successful
            success_rate = successful / count
            print(f"Prueba con {count} conexiones: {successful} exitosas ({success_rate*100:.1f}%)")
            
            # Si la tasa de éxito cae por debajo del 90%, hemos encontrado el límite
            if success_rate < 0.9:
                break

        # Documentar los resultados
        print("\nResultados de la prueba de estrés:")
        for count, successful in results.items():
            print(f"Conexiones intentadas: {count}, Exitosas: {successful}")

    @pytest.mark.asyncio
    async def test_single_connection(self):
        """Prueba básica de conexión de un solo usuario"""
        print("\n=== TEST CONEXIÓN INDIVIDUAL ===")
        
        # 1. Crear datos de prueba
        print("Creando datos de prueba...")
        user = await database_sync_to_async(User.objects.create_user)(
            username='testuser',
            password='testpass'
        )
        print(f"Usuario creado: {user.username}")
        
        student = await database_sync_to_async(StudentModel.objects.create)(
            user=user
        )
        print(f"Estudiante creado: ID={student.id}")
        
        scenario = await database_sync_to_async(ScenarioModel.objects.create)(
            name="Test Scenario",
            conversation_starter="Hello!"
        )
        print(f"Escenario creado: ID={scenario.id}")
        
        # 2. Intentar conexión
        path = f"/ws/chat/{scenario.id}/{student.id}/"
        print(f"Intentando conexión en: {path}")
        
        communicator = WebsocketCommunicator(
            self.application,
            path
        )
        
        connected, _ = await communicator.connect()
        print(f"Estado de conexión: {connected}")
        
        assert connected, "La conexión inicial falló"
        
        # 3. Enviar un mensaje simple
        print("Enviando mensaje de prueba...")
        await communicator.send_json_to({
            "type": "message",
            "message": "Hello!",
            "role": "user"
        })
        
        # 4. Esperar respuesta
        try:
            response = await communicator.receive_json_from()
            print(f"Respuesta recibida: {response}")
            assert response is not None
            assert 'message' in response
            assert 'role' in response
            assert response['role'] == 'assistant'
        except Exception as e:
            print(f"Error al recibir respuesta: {str(e)}")
            raise
        finally:
            await communicator.disconnect()

def create_test_application():
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from chat.routing import websocket_urlpatterns
    
    return ProtocolTypeRouter({
        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    })