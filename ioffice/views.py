from django.http import HttpResponse
from django.template import loader

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework.decorators import api_view
 
# from django.contrib.auth.decorators import login_required
from .services import IofficeService

import json
import calendar
from datetime import datetime

def information(request):
    template = loader.get_template('ioffice/information.html')
    Ioffice = IofficeService()
    context = Ioffice.get_general_information()
    context['update_date'] = f"{datetime.now().month}/{datetime.now().year}"
    return HttpResponse(template.render(context, request))

def document(request):
    template = loader.get_template('ioffice/document.html')

    search_query = request.GET.get('search_query', '')
    start_date = request.GET.get('from_date', False)
    end_date = request.GET.get('to_date', False)

    Ioffice = IofficeService()

    units = Ioffice.get_units(0, 100, search_query=search_query)

    unit_ids = ', '.join([x['ma'] for x in units])
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
    else:
        start_date = datetime(current_year, current_month-1, 1, 0, 0, 0).strftime('%d/%m/%Y')

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
    else:
        end_date = datetime.now().strftime('%d/%m/%Y')

    documents = Ioffice.request_documents(start_date, end_date, unit_ids)

    for d in documents:
        d['tong_so_di'] = int(d['tong_so_di'])
        d['tong_so_den'] = int(d['tong_so_den'])
        d['total'] = d['tong_so_di'] + d['tong_so_den']
    context = {
        'documents': documents,
        'units_count': len(Ioffice.get_units(limit=0)),
        'start_date': datetime(current_year, current_month-1, 1, 0, 0, 0).strftime('%Y-%m-%d'),
        'end_date': datetime.now().strftime('%Y-%m-%d'),
        'search_query': search_query
    }
    return HttpResponse(template.render(context, request))