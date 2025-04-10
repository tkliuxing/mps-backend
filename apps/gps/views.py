from django.shortcuts import render
from django.http import HttpResponse
from .serializers import PointSerializer
from .utils import refresh_last_point

def gps_test(request) -> HttpResponse:
    if request.method == 'GET':
        return render(request, 'gps/gps_test.html')
    if request.method == 'POST':
        serial = PointSerializer(data=request.POST)
        if serial.is_valid():
            instance = serial.save()
            refresh_last_point(instance.sys_id, instance.org_id, [instance.sn])
            return HttpResponse('{"success":true}')
        else:
            return HttpResponse(f'{{"success":false, "errors":{serial.errors}}}', status=400)
    return HttpResponse('', status=400)
