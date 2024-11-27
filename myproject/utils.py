import pymongo, environ
from werkzeug.security import generate_password_hash

env = environ.Env()
environ.Env.read_env()

DATABASE_URL = env('DATABASE_URL')
db_name = env('db_name')
db_collection = env('db_collection')
client = pymongo.MongoClient(DATABASE_URL)

db = client[db_name]
collection = db[db_collection]

hashed_password = generate_password_hash("CSUB1234")

# testing
document_1 = {
    "username": "avu",
    "password": hashed_password,
}

collection.insert_one(document_1)
