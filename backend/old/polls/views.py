from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import answer
from . import domains
from django.middleware.csrf import get_token

from django.conf import settings

def x(request):
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
    domain_id = data["domain_id"]
    print("domain_id", domain_id)
    print("query", query)
    res = answer.get_answer(domain_id, query)
    return JsonResponse(res)

def get_domains(request):
    res = domains.get_domains()
    print(res)
    return JsonResponse(res, safe = False)
