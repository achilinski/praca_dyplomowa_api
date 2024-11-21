from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ChatMessage


# Create your views here.


@api_view(['GET'])
def get_all_chat_rooms(request):
    chat_data=[]
    try:
        chats = ChatMessage.objects.all()
    except chats.DoesNotExist:
        return Response({"error":"chats not found"}, status=status.HTTP_404_NOT_FOUND)
    
    for chat in chats:
        chat_data.append({chat.room_name})

    return Response({"chats":chat_data}, status=status.HTTP_200_OK)
