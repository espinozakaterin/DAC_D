
import os
import django
import json
from django.test import RequestFactory
from django.http import JsonResponse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

from CONTROLSUM.views.ControlSumView import get_suministros_data

def test():
    rf = RequestFactory()
    
    # Test with stock_bajo=1
    request = rf.post('/get/suministros/data', {'stock_bajo': '1'})
    response = get_suministros_data(request)
    data = json.loads(response.content)
    print(f"STOCK_BAJO=1 COUNT: {len(data.get('data', []))}")
    if len(data.get('data', [])) > 0:
        print(f"FIRST ITEM: {data['data'][0]['nombre']} (Stock: {data['data'][0]['cantidad_stock']}, Min: {data['data'][0]['cantidad_min']})")

    # Test without filter
    request_all = rf.post('/get/suministros/data', {})
    response_all = get_suministros_data(request_all)
    data_all = json.loads(response_all.content)
    print(f"NO_FILTER COUNT: {len(data_all.get('data', []))}")

if __name__ == "__main__":
    test()
