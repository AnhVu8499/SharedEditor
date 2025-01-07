from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from werkzeug.security import check_password_hash
import environ, pymongo, json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env_file = BASE_DIR / ".env"
environ.Env.read_env(env_file=env_file)

def login_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            username = body.get('username')
            password = body.get('password')
        except json.JSONDecodeError:
             return JsonResponse({'message': 'Invalid JSON'}, status=400)
        if not username or not password:
             return JsonResponse({'message': 'Username and password are required'}, status=400)

        # Connect to MongoDB            
        DATABASE_URL = env('DATABASE_URL')
        db_name = env('db_name')
        db_collection = env('db_collection')

        client = pymongo.MongoClient(DATABASE_URL)
        db = client[db_name]
        collection = db[db_collection] 

        # Find user
        user = collection.find_one({ 'username': username })
        if user and check_password_hash(user['password'], password):
            return JsonResponse({'message': '"Password is valid"'})
        else:
            return JsonResponse({'message': '"Invalid password"'}, status=401)
    else:
        return JsonResponse({'message': 'Only POST method is allowed'}, status=405)