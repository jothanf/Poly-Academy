from django.shortcuts import render
from django.http import JsonResponse
from dashboard.models import ScenarioModel
from dashboard.IA.openAI import AIService
import json
from django.views.decorators.csrf import csrf_exempt

def select_scenario(request):
    scenarios = ScenarioModel.objects.all()
    return render(request, 'select_scenario.html', {'scenarios': scenarios})

#def chat_room(request, scenario_id):
#    try:
#        scenario = ScenarioModel.objects.get(id=scenario_id)
#        return render(request, 'chatroom.html', {'scenario': scenario})
#    except ScenarioModel.DoesNotExist:
#        return render(request, '404.html', status=404)  # Manejo de error 404

@csrf_exempt
def chat_ai(request):
    if request.method == 'POST':
        try:
            # Obtener o inicializar el historial de la sesión
            if 'chat_history' not in request.session:
                request.session['chat_history'] = []
            
            data = json.loads(request.body)
            user_message = data.get('message')
            
            # Obtener el historial actual
            conversation_history = request.session.get('chat_history', [])
            
            # Si es la primera interacción, agregar el contexto del sistema
            if not conversation_history:
                conversation_history.append({
                    "role": "system",
                    "content": """Eres un profesor de inglés amable y paciente. 
                    Tu objetivo es ayudar a los estudiantes con sus dudas sobre el idioma inglés,
                    proporcionando explicaciones claras y ejemplos útiles."""
                })
            
            # Agregar el mensaje del usuario al historial
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Crear una instancia de AIService
            ai_service = AIService()
            
            # Obtener respuesta usando todo el historial
            response = ai_service.chat_with_gpt(user_message, conversation_history)
            
            # Agregar la respuesta al historial
            conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Actualizar el historial en la sesión
            request.session['chat_history'] = conversation_history
            request.session.modified = True
            
            return JsonResponse({'response': response})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return render(request, 'chat_ai.html')
