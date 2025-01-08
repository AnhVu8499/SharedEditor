from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from werkzeug.security import generate_password_hash
import json, environ, pymongo, os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
# env = environ.Env()
# env_file = BASE_DIR / ".env"
# environ.Env.read_env(env_file=env_file)

@csrf_exempt  # Only for testing; remove in production
def signup_view(request):
    if request.method == 'POST':
        # Connect to MongoDB            
        DATABASE_URL = os.getenv('DATABASE_URL')
        db_name = os.getenv('db_name')
        db_collection = os.getenv('db_collection')

        client = pymongo.MongoClient(DATABASE_URL)
        db = client[db_name]
        collection = db[db_collection] 
        try:
            body = json.loads(request.body)
            username = body.get('username')
            password = body.get('password')
            hashed_password = generate_password_hash(password)

            user = collection.find_one({ 'username': username })
            if user:
                return JsonResponse({'message': '"Username already exists"'})
            else:
                newuser = {
                    "username": username,
                    "password": hashed_password,
                }
                collection.insert_one(newuser)
                return JsonResponse({'message': '"Good to go"'})
        except json.JSONDecodeError:
             return JsonResponse({'message': 'Invalid JSON'}, status=400)
        if not username or not password:
             return JsonResponse({'message': 'Username and password are required'}, status=400)
    else:
        return JsonResponse({'message': 'Only POST method is allowed'}, status=405)

    