from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import answer
from django.middleware.csrf import get_token

from django.conf import settings

def x(request):
    print(settings.BASE_DIR)
    print("request", request)
    return HttpResponse("hello")

def get_csrf_token(request):
    res = {"token": get_token(request)}
    return JsonResponse(res)

@csrf_exempt 
def index(request):
    body = request.body
    print("body", body)
    data = json.loads(body)
    query = data["query"]
    print("query", query)
    res = answer.get_answer(query)
    return JsonResponse(res)

