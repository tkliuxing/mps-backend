import os
import subprocess
import re
import requests
import logging
from django.conf import settings
from django.core.files import File

logger = logging.getLogger('django.server')

def convert_to(folder, source, timeout=None):
    if getattr(settings, 'REMOTE_CONVERT', False):
        return remote_convert(folder, source)
    args = [libreoffice_exec(), '--headless', '--convert-to', 'pdf', '--outdir', folder, source]

    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())

    if filename is None:
        logger.error("failed LibreOfficeError:{}".format(' '.join(args)))
        raise LibreOfficeError(process.stdout.decode())
    else:
        return filename.group(1)


def remote_convert(folder, source):
    remote_url = getattr(settings, 'REMOTE_CONVERT')
    if not remote_url:
        raise LibreOfficeError('REMOTE_CONVERT settings not configured!')
    fp = open(source, 'rb')
    file_data = fp.read()
    fp.close()
    resp = requests.post(f'{remote_url}/convert_docx/', files={'file': file_data})
    if resp.status_code != 200:
        logger.error("failed LibreOfficeError:{}".format(resp.text))
        raise LibreOfficeError('REMOTE_CONVERT settings not configured!')
    file_url = resp.text
    filename = os.path.split(file_url)[1]
    resp = requests.get(f'{remote_url}/uploads/{file_url}')
    os.makedirs(folder, exist_ok=True)
    with open(folder+'/'+filename, 'wb') as ff:
        ff.write(resp.content)
    return folder+'/'+filename


def libreoffice_exec():
    return settings.LIBREOFFICE_PATH


class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output


# if __name__ == '__main__':
#     print('Converted to ' + convert_to(sys.argv[1], sys.argv[2]))
