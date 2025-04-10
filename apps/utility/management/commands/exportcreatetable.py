import subprocess
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "导出建表语句"

    def add_arguments(self, parser):
        parser.add_argument('--file', dest="file", default=None, type=str,
                            help='输出到指定文件')
        parser.add_argument('--partitioned', dest='partitioned', action='store_true',
                            help='导出分区表'),

    def handle(self, *args, **options):
        from formtemplate import migrations
        has_pg_dump = subprocess.run("which pg_dump".split(), stdout=subprocess.PIPE)
        if has_pg_dump.returncode != 0:
            self.stdout.write("未找到 pg_dump!")
            return
        db_name = settings.DATABASES['default']['NAME']
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']
        db_user = settings.DATABASES['default']['USER']
        db_pwd = settings.DATABASES['default']['PASSWORD']

        cmd_line = [
            "pg_dump", "-h", db_host, "-p", str(db_port), "-U", db_user,
            "-s", "-O", "-x", "--no-comments", "--no-publications", "--no-security-labels",
            "--no-tablespaces",
        ]
        if not options['partitioned']:
            cmd_line.extend(["--exclude-table", "formtemplate_formdata*"])
        cmd_line.append(db_name)
        dump_data_process = subprocess.Popen(
            cmd_line,
            env={"PGPASSWORD": db_pwd, **os.environ},
            stdout=subprocess.PIPE
        )
        out = dump_data_process.stdout.readlines()
        lines = []
        for l in out:
            l = l
            if l.startswith(b'--') or not l or l.startswith(b'\n'):
                continue
            if l.startswith(b'SET') or l.startswith(b'SELECT'):
                continue
            if l.startswith(b'CREATE EXTENSION'):
                continue
            if l.startswith(b'CREATE INDEX') and b'_like ON' in l:
                continue
            nl = l.replace(b' USING btree', b'')
            lines.append(nl)
        if not options['partitioned']:
            sql_path = Path(migrations.__file__).parent / 'create_formdata_onetable.sql'
        else:
            sql_path = None
        if options['file']:
            with open(options['file'], 'wb') as f:
                for l in lines:
                    f.write(l)
                if sql_path:
                    with open(sql_path, 'rb') as sql_file:
                        f.write(sql_file.read())
        else:
            for l in lines:
                self.stdout.write(l.decode())
            if sql_path:
                with open(sql_path, 'rb') as sql_file:
                    self.stdout.write(sql_file.read().decode())
