from django.urls import path
from .views import (
    start_conversation,
    send_message,
    end_conversation, 
    list_conversations,
    get_conversation,
    edit_conversation_title,
    delete_conversation,
    intelligent_query,
)

urlpatterns = [
    path("chat/start/", start_conversation),
    path("chat/send/", send_message),
    path("chat/end/", end_conversation),
    path("chat/list/", list_conversations),
    path("chat/<int:pk>/", get_conversation),
    path("chat/<int:pk>/edit/", edit_conversation_title),
    path("chat/<int:pk>/delete/", delete_conversation),
    path("chat/query/", intelligent_query),
]