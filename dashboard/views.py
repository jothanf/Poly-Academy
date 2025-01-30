
"""
class FormattedTextViewSet(viewsets.ModelViewSet):
    queryset = FormattedTextModel.objects.all()
    serializer_class = FormattedTextModelSerializer

    def get_queryset(self):
        queryset = FormattedTextModel.objects.all()
        class_id = self.request.query_params.get('class_id', None)
        if class_id is not None:
            queryset = queryset.filter(class_model_id=class_id)
        return queryset.order_by('-created_at')  # Ordenar por fecha de creación descendente

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Obtener el límite de la query params
        limit = request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
            
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Textos formateados obtenidos exitosamente',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        try:
            print("Datos recibidos:", request.data)  # Debug
            # Validaciones explícitas
            if 'class_model' not in request.data:
                return Response({
                    'status': 'error',
                    'message': 'El campo class_model es requerido',
                    'errors': {'class_model': ['Este campo es requerido']}
                }, status=status.HTTP_400_BAD_REQUEST)

            if 'content' not in request.data:
                return Response({
                    'status': 'error',
                    'message': 'El campo content es requerido',
                    'errors': {'content': ['Este campo es requerido']}
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print("Errores de validación:", serializer.errors)
                return Response({
                    'status': 'error',
                    'message': 'Error de validación',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            
            return Response({
                'status': 'success',
                'message': 'Texto formateado creado exitosamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print("Error detallado:", traceback.format_exc())  # Debug
            return Response({
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }, status=500)
"""
      