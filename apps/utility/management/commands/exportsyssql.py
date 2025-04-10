import subprocess
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from utility.sql_export import export_sql_insert


class Command(BaseCommand):
    help = "导出系统数据"

    def add_arguments(self, parser):
        parser.add_argument('--file', dest="file", default=None, type=str,
                            help='输出到指定文件')
        parser.add_argument('--sys_id', dest='sys_id', default=None, type=int,
                            help='导出SYSID')
        parser.add_argument('--org_id', dest='org_id', default=None, type=int,
                            help='导出ORGID')
        parser.add_argument('--include_cms', dest='include_cms', action='store_true',
                            help='导出CMS相关数据')

    def handle(self, *args, **options):
        prefix_str = """SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', 'public', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
"""
        sql_lines = export_sql_insert(options['sys_id'], options['org_id'], options['include_cms'])
        if options['file']:
            with open(options['file'], 'w') as f:
                f.write(prefix_str)
                f.write(sql_lines)
        else:
            self.stdout.write(prefix_str + '\n')
            for l in sql_lines.splitlines():
                self.stdout.write(l + '\n')
