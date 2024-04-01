from django.urls import path
from main.views import IndexView, clear_cache, clear_session

app_name = 'main_url'

urlpatterns = [
    path('', IndexView.as_view(), name='main_index'),
    path('clear_cache/', clear_cache, name='clear_cache'),
    path('clear_session/', clear_session, name='clear_session'),
    ]
