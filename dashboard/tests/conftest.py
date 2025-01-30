import pytest
from channels.testing import WebsocketCommunicator
from pmback.asgi import application

@pytest.fixture
async def communicator():
    """Fixture para inicializar el WebsocketCommunicator"""
    communicator = WebsocketCommunicator(
        application=application,
        path="/ws/chat/test_room/1/"  # Ajusta la ruta según tu routing.py
    )
    connected, subprotocol = await communicator.connect()
    assert connected, "No se pudo conectar al WebSocket"
    yield communicator
    await communicator.disconnect() 