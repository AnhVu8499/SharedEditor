from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, asyncio
from .consumer import EditorConsumer

@csrf_exempt
def save_to_db_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            username = body.get('username')

            if not username:
                return JsonResponse({"message": "Username is required"}, status=400)
                
            result = asyncio.run(EditorConsumer().save_db(username))
            
            return JsonResponse({"message": "Save successful"}) 
        except Exception:
            return JsonResponse({"message": "Error occurred"}, status=500)
    return JsonResponse({"message": "Invalid request method"}, status=405)
