from django.urls import path
from .views import handle_interaction, send_message

urlpatterns = [
    path('send-message/', send_message, name='send-message'),
    path('handle-interaction/', handle_interaction, name='handle-interaction'),
]
