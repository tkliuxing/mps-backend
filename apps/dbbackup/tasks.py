from io import StringIO
from celery import shared_task


@shared_task
def backup_database():
    from django.core import management
    from django.core.management.base import OutputWrapper
    from dbbackup.management.commands import dbbackup
    cmd = dbbackup.Command()
    out = StringIO()
    cmd.stdout = OutputWrapper(out)
    management.call_command(cmd, compress=True)
    output = cmd.stdout.getvalue()
    out.close()
    return output


@shared_task
def restore_database(input_filename):
    from django.core import management
    from django.core.management.base import OutputWrapper
    from dbbackup.management.commands import dbrestore
    cmd = dbrestore.Command()
    out = StringIO()
    cmd.stdout = OutputWrapper(out)
    management.call_command(cmd, input_filename=input_filename, uncompress=True)
    output = cmd.stdout.getvalue()
    out.close()
    return output