from .models import Property

def agent_properties(request):
    if request.user.is_authenticated and request.user.user_type == 'agent':
        properties = Property.objects.filter(agent=request.user).order_by('-created_at')
    else:
        properties = None
    return {'agent_properties': properties}