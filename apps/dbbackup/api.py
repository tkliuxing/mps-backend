from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.response import HttpResponse
from .storage import get_storage
from . import utils

class DBBackupAPI(APIView):
    def get(self, request):
        storage = get_storage()
        options = {
            'content_type': 'db',
        }
        filenames = storage.list_backups(**options)
        data = [
            {
                "datetime": utils.filename_to_date(filename).strftime("%x %X"),
                "name": filename,
            }
            for filename in filenames
        ]
        return Response(data)
    
    def post(self, request):
        from .tasks import backup_database
        backup_database.delay()
        return Response({'message': '任务已经提交，请稍后查看备份文件'})


class DBRestoreAPI(APIView):
    def get(self, request):
        from .management.commands import dbrestore
        file_name = request.GET.get('filename')
        if not file_name:
            return Response({'message': '请提供文件名'})
        cmd = dbrestore.Command()
        cmd.storage = get_storage()
        cmd.filename = file_name
        cmd.path = None
        cmd.servername = None
        input_filename, input_file = cmd._get_backup_file()
        resp = HttpResponse(input_file, content_type='application/octet-stream')
        resp['Content-Disposition'] = 'attachment; filename={}'.format(input_filename)
        return resp
    
    def post(self, request):
        from .tasks import restore_database
        file_name = request.data.get('filename')
        restore_database.delay(file_name)
        return Response({'message': '任务已经提交，请稍后刷新查看'})
