from django.shortcuts import render
from dashboard.models import ScenarioModel

def select_scenario(request):
    scenarios = ScenarioModel.objects.all()
    return render(request, 'select_scenario.html', {'scenarios': scenarios})

def chat_room(request, scenario_id):
    try:
        scenario = ScenarioModel.objects.get(id=scenario_id)
        return render(request, 'chatroom.html', {'scenario': scenario})
    except ScenarioModel.DoesNotExist:
        return render(request, '404.html', status=404)  # Manejo de error 404
