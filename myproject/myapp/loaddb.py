from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, asyncio
from .consumer import EditorConsumer

def load_from_db_view(request):
    if request.method == 'GET':
        try:
            username = request.GET.get('username')
            if not username:
                return JsonResponse({"message": "Username is required"}, status=400)

            result = asyncio.run(EditorConsumer().load_db(username))
            if result.get('success'):
                return JsonResponse({"message": "Load successful", "content": result.get('content')})
            else:
                return JsonResponse({"message": result.get('message')}, status=400)
            
        except Exception:
            return JsonResponse({"message": "Error occurred"}, status=500)
    return JsonResponse({"message": "Invalid request method"}, status=405)
