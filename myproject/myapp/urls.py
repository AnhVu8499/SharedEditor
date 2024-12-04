from django.urls import path
from .signin import login_view
from .signup import signup_view
from .savedb import save_to_db_view

urlpatterns = [
    path('login/', login_view),
    path('signup/', signup_view),
    path('save-to-db', save_to_db_view),
]