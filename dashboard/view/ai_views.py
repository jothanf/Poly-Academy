from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..serializers import AskOpenAISerializer, TextToSpeechRequestSerializer, TextToSpeechResponseSerializer, SuccessResponseSerializer, ErrorResponseSerializer, TranscribeAudioSerializer
from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import tempfile
import logging
from ..IA.openAI import AIService
from ..IA.imgGen import ImageGenerator
from drf_spectacular.utils import extend_schema, OpenApiResponse
import os
import uuid


logger = logging.getLogger(__name__)

class AskOpenAIView(generics.GenericAPIView):
    serializer_class = AskOpenAISerializer

    def post(self, request):
        logger.debug("Recibida solicitud en AskOpenAIView")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ai_service = AIService()
            question = serializer.validated_data['question']
            
            answer = ai_service.chat_with_gpt(question)
            
            return Response({
                'status': 'success',
                'answer': answer
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status': 'error',
            'message': 'Error al procesar la solicitud',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def translate_message(request):
    try:
        message = request.data.get('message')
        if not message:
            return Response({
                'status': 'error',
                'message': 'Se requiere un mensaje para traducir'
            }, status=status.HTTP_400_BAD_REQUEST)

        ai_service = AIService()
        translation = ai_service.translate_to_spanish(message)
        
        return Response({
            'status': 'success',
            'translation': translation
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      
@csrf_exempt
def img_gen(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
          
            prompt = data.get('prompt')
            if not prompt:
                return JsonResponse({'error': 'No se proporcionó un prompt'}, status=400)
            
            generator = ImageGenerator()
            result = generator.generate_image(prompt)
            
            if result['success']:
                return JsonResponse({'url': result['url']})
            else:
                return JsonResponse({'error': result['error']}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'img_gen.html')

@extend_schema(
    request=TextToSpeechRequestSerializer,
    responses={
        200: TextToSpeechResponseSerializer,
        400: OpenApiResponse(
            response=TextToSpeechResponseSerializer,
            description='Error en la solicitud'
        )
    }
)
@api_view(['POST'])
def text_to_speech(request):
    texto = request.data.get('texto')
    voz = request.data.get('voz', 'alloy')
    
    if not texto:
        return Response({
            'status': 'error', 
            'message': 'El texto es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Crear el directorio temporal si no existe
        audio_dir = 'media/temp_audio'
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generar un nombre único para el archivo
        file_uuid = uuid.uuid4()
        output_file = f"{audio_dir}/tts_{file_uuid}.mp3"
        
        ai_service = AIService()
        result = ai_service.text_to_speech(texto, voice=voz, output_file=output_file)
        
        if result:
            audio_url = f"/media/temp_audio/{os.path.basename(output_file)}"
            return Response({
                'status': 'success',
                'message': 'Audio generado exitosamente',
                'audio_url': audio_url
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Error al generar el audio'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(f"Error en text_to_speech: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    request=TranscribeAudioSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer
    }
)
@api_view(['POST'])
def transcribe_audio(request):
    try:
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response(
                {'error': 'No se proporcionó archivo de audio'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Guardar el archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            for chunk in audio_file.chunks():
                temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        try:
            # Usar el servicio AI para transcribir
            ai_service = AIService()
            result = ai_service.client.audio.transcriptions.create(
                model="whisper-1",
                file=open(temp_audio_path, "rb")
            )

            # Analizar la pronunciación después de la transcripción
            pronunciation_analysis = ai_service.analyze_pronunciation(result.text)

            return Response({
                'status': 'success',
                'data': {
                    'transcription': result.text,
                    'pronunciation_analysis': pronunciation_analysis
                }
            })

        finally:
            # Limpiar el archivo temporal
            try:
                os.unlink(temp_audio_path)
            except Exception as e:
                print(f"Error al eliminar archivo temporal: {e}")

    except Exception as e:
        print(f"Error en transcribe_audio: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
