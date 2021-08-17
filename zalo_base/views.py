from django.http import HttpResponse
from django.template import loader

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework.decorators import api_view
 
from .services import ZaloService
from ccos.services import process_content

import json

def index(request):
    template = loader.get_template('zalo_base/index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def ccos(request):
    template = loader.get_template('zalo_base/ccos_manage.html')
    context = {}
    return HttpResponse(template.render(context, request))

def regist_payment(request):
    template = loader.get_template('zalo_base/regist_payment.html')
    context = {}
    return HttpResponse(template.render(context, request))

def page_404(request):
    template = loader.get_template('zalo_base/404.html')
    context = {}
    return HttpResponse(template.render(context, request))

@api_view(['POST'])
def submit_regist_payment(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'POST'):
        message = f"Data is not valid"
        datas = json.loads(request.body)
        if datas.get('user_id'):
            result = ZaloService().submit_regist_payment(datas)
            return JsonResponse(result)
    return JsonResponse({
        'success': 0, 
        'message': message
        })

@api_view(['GET'])
def get_client_by_user_id(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'GET'):
        message = f"Data is not valid"
        datas = request.GET
        if datas.get('user_id'):
            result = ZaloService().get_client_by_user_id(datas.get('user_id'))
            return JsonResponse(result)
    return JsonResponse({
        'success': 0, 
        'message': message
        })

@api_view(['POST'])
def follow_hook(request):
    if (request.method == 'POST'):
        try:
            datas = json.loads(request.body)
            event = datas.get('event_name', False)
            if event:
                result = ZaloService().action_by_event(event, datas)
                return JsonResponse(result)
        except Exception as err:
            return JsonResponse({
                'success': 0, 
                'message': f"Internal Error: {err}"
            })

    return JsonResponse({
        'success': 0, 
        'message': f"Request method {request.method} is not allowed!"
        })

@api_view(['GET'])
def get_client_by_user_id(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'GET'):
        message = f"Data is not valid"
        datas = request.GET
        if datas.get('user_id'):
            result = ZaloService().get_client_by_user_id(datas.get('user_id'))
            return JsonResponse(result)
    return JsonResponse({
        'success': 0, 
        'message': message
        })

@api_view(['GET', 'POST'])
def api_ccos(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'GET'):
        message = f"Data is not valid"
        datas = request.GET
        if datas.get('state'):
            result = process_content(datas.get('state'), datas)
            return JsonResponse(result)
    elif request.method == 'POST':
        datas = json.loads(request.body)
        if datas.get('state'):
            result = process_content(datas.get('state'), datas)
            return JsonResponse(result)
    return JsonResponse({
            'success': 0, 
            'message': message
        })

@api_view(['GET'])
def test(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'GET'):
        datas = request.GET
        OracleService = ZaloService().get_oracle_service()
        result = OracleService.get_payment_debt("6046163127961711684")
        return JsonResponse(dict(result=result))
    return JsonResponse({
        'success': 0, 
        'message': message
        })