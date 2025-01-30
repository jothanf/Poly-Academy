from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import ClassModel, ClassContentModel
from ..serializers import ClassModelSerializer, ClassContentModelSerializer
from django.shortcuts import render
from drf_spectacular.utils import extend_schema


@extend_schema(exclude=True)
@api_view(['GET', 'POST'])
def prueva_json(request):
    if request.method == 'GET':
        try:
            content_type = request.query_params.get('content_type')
            contents = ClassContentModel.objects.all()
            if content_type:
                contents = contents.filter(content_type=content_type)
            
            serializer = ClassContentModelSerializer(contents, many=True)
            
            if request.headers.get('Accept') == 'application/json':
                return Response({
                    'status': 'success',
                    'data': serializer.data
                })
            
            return render(request, 'prueva_json.html')
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)

    elif request.method == 'POST':
        try:
            data = request.data
            
            # Validar class_id
            try:
                class_instance = ClassModel.objects.get(id=data.get('class_id'))
            except ClassModel.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Clase no encontrada'
                }, status=400)

            # Crear el objeto de contenido
            content_data = {
                'class_id': class_instance.id,  # Cambiado para usar el ID en lugar del objeto
                'content_type': 'picture_matching_knowledge_check',
                'tittle': data.get('title'),
                'content_details': data.get('content_details', {})
            }

            # Crear el serializer con los datos
            serializer = ClassContentModelSerializer(data=content_data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Contenido creado exitosamente',
                    'data': serializer.data
                })
            else:
                # Devolver errores detallados de validación
                return Response({
                    'status': 'error',
                    'message': 'Error de validación',
                    'errors': serializer.errors,
                    'received_data': content_data  # Agregar datos recibidos para debugging
                }, status=400)

        except Exception as e:
            import traceback
            return Response({
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()  # Agregar traceback para debugging
            }, status=500)