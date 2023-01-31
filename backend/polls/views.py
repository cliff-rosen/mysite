from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from . import answer

from django.middleware.csrf import get_token

def get_csrf_token(request):
    token = get_token(request)
    return HttpResponse(token)

def index(request):
    query = "describe this company"
    body = request.body
    print("body", body)
    data = json.loads(body)
    query = data["query"]
    print("query", query)
    res = answer.get_answer(query)
    return JsonResponse(res)

