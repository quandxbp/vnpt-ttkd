from django.http import HttpResponse
from django.template import loader

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework.decorators import api_view
 
from .services import ZaloService

import json

def index(request):
    template = loader.get_template('zalo_base/index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def location(request, zuser_id):
    template = loader.get_template('zalo_base/location.html')
    context = {
        'zuser_id': zuser_id
    }
    return HttpResponse(template.render(context, request))

@api_view(['GET','POST'])
def site(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'POST'):
        datas = json.loads(request.body)
        if datas.get('site'):
            result = ZaloService().set_site(datas.get('site'))
            return JsonResponse(result)
    elif (request.method == 'GET'):
        result = ZaloService().get_site()
        return JsonResponse({
            'production_site': "https://kiemdich.binhphuoc.gov.vn",
            'current_site': result,
        })
    return JsonResponse({
        'success': 0, 
        'message': message
        })

@api_view(['POST'])
def message(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'POST'):
        datas = json.loads(request.body)
        if datas.get('zuser_id'):
            result = ZaloService().post_message(datas.get('zuser_id') ,datas.get('message', False))
            return JsonResponse(result)
        elif datas.get('messages'):
            result = ZaloService().post_multiple_message(datas.get('messages'))
            return JsonResponse(result)
        message = 'Zalo User ID is not provided'
    return JsonResponse({
        'success': 0, 
        'message': message
        })

@api_view(['GET'])
def location_confirm(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'GET'):
        datas = request.GET
        if datas.get('zuser_id'):
            result = ZaloService().send_confirm_location_message(datas.get('zuser_id') ,datas)
            return JsonResponse(result)
        message = 'Zalo User ID is not provided'
    return JsonResponse({
        'success': 0, 
        'message': message
        })

@api_view(['POST'])
def declare_confirm(request):
    message = f"Request method {request.method} is not allowed!"
    if (request.method == 'POST'):
        datas = json.loads(request.body)
        if datas.get('zuser_id'):
            result = ZaloService().send_confirm_message(datas.get('zuser_id') ,datas)
            return JsonResponse(result)
        message = 'Zalo User ID is not provided'
    return JsonResponse({
        'success': 0, 
        'message': message
        })

@api_view(['GET'])
def checkpoint_confirm(request):
    if (request.method == 'GET'):
        datas = request.GET
        if datas.get('phone'):
            result = ZaloService().send_confirm_at_checkpoint(datas.get('phone'))
            return JsonResponse(result)
    return JsonResponse({
        'success': 0, 
        'message': f"Request method {request.method} is not allowed!"
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


