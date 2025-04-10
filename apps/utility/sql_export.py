from django.db import connection
from .dbtables import (
    SYSTEM_TABLES,
    DEFINE_TABLES,
    CMS_TABLES,
    DATA_TABLES,
    DEL_DATA_TABLES,
    RELATED_TABLES,
    IGNORE_EXPORT_TABLES,
)


SQL_HEAD = """
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
SET schema 'public';
"""


def export_sql_insert(table_name: str, sys_id: int = None, org_id: int = None):
    """导出指定表的insert语句，根据sys_id和org_id拼装where条件"""
    sys_id = int(sys_id) if sys_id else None
    org_id = int(org_id) if org_id else None
    insert_sql_lines = []
    with connection.cursor() as c:
        try:
            table_description = connection.introspection.get_table_description(c, table_name)
        except:
            raise Exception(f"table {table_name} not found")
        field_dict = {i.name: None for i in table_description}
        select_sql = None
        if table_name in RELATED_TABLES:
            rel_table = RELATED_TABLES[table_name][0]
            rel_field = RELATED_TABLES[table_name][1]
            rel_table_description = connection.introspection.get_table_description(c, rel_table)
            rel_field_dict = {i.name: None for i in rel_table_description}
            if sys_id is not None and org_id is not None and 'sys_id' in rel_field_dict and 'org_id' in rel_field_dict:
                select_sql = f"SELECT * FROM {table_name} WHERE {rel_field} in (select id from {rel_table} WHERE sys_id={sys_id} AND (org_id={org_id} OR org_id=0))"
            elif sys_id is not None and 'sys_id' in rel_field_dict:
                select_sql = f"SELECT * FROM {table_name} WHERE {rel_field} in (select id from {rel_table} WHERE sys_id={sys_id})"
            else:
                raise Exception(f"sys_id is required for table {table_name}")
        else:
            select_sql = f"SELECT * FROM {table_name}"
            if sys_id is not None and 'sys_id' in field_dict:
                select_sql = select_sql + f" WHERE sys_id={sys_id}"
                if org_id is not None and 'org_id' in field_dict:
                    select_sql = select_sql + f" AND (org_id={org_id} or org_id=0)"
        order_by_sql = ""
        if 'tree_id' in field_dict:
            if org_id is None and 'org_id' in field_dict:
                order_by_sql = " ORDER BY org_id, tree_id, level"
            else:
                order_by_sql = " ORDER BY tree_id, level"
        elif 'id' in field_dict:
            if org_id is None and 'org_id' in field_dict:
                order_by_sql = " ORDER BY org_id, id"
            else:
                order_by_sql = " ORDER BY id"
        select_sql = select_sql + order_by_sql
        insert_sql_lines.append(f"\n-- table: {table_name}\n")
        insert_sql_lines.append(custom_export_sql_insert_with_cursor(table_name, select_sql, c))
        insert_sql_lines.append("")
    return "\n".join(insert_sql_lines)


def custom_export_sql_insert_with_cursor(table_name: str, sql: str, cursor):
    """使用指定语句导出指定表的insert语句"""
    insert_sql_lines = []
    try:
        connection.introspection.get_table_description(cursor, table_name)
    except:
        raise Exception(f"table {table_name} not found")
    cursor.execute(sql)
    columns = []
    for col in cursor.description:
        columns.append(f'"{col[0]}"')
    columns = ",".join(columns)
    data = cursor.fetchall()
    for line in data:
        s_col = ",".join(["%s"] * len(cursor.description))
        query = f"INSERT INTO {table_name} ({columns}) VALUES({s_col});"
        try:
            insert_sql_lines.append(
                cursor.mogrify(query, line).decode()
            )
        except Exception as e:
            print(query, '\n', line)
            raise e
    return "\n".join(insert_sql_lines)


def custom_export_sql_insert(table_name: str, sql: str):
    with connection.cursor() as c:
        return custom_export_sql_insert_with_cursor(table_name, sql, c)


def export_system_sql(sys_id, include_parameters=False):
    insert_sql_lines = []
    related_tables = RELATED_TABLES
    join_sql = "SELECT A.* FROM {table_name} A inner join {rel_table} ss on A.{rel_field} = ss.id WHERE ss.sys_id={sys_id} ORDER BY A.id"
    for table_name in SYSTEM_TABLES:
        if not include_parameters and table_name == 'parameter_parameters':
            continue
        try:
            if table_name in related_tables:
                rel_table = related_tables[table_name][0]
                rel_field = related_tables[table_name][1]
                sql = join_sql.format(table_name=table_name, rel_table=rel_table, rel_field=rel_field, sys_id=sys_id)
                insert_sql_lines.append(custom_export_sql_insert(table_name, sql))
                continue
            insert_sql_lines.append(export_sql_insert(table_name, sys_id))
        except Exception as e:
            print(table_name)
            raise e
    return "\n".join(insert_sql_lines)


def export_system_del_sql(sys_id, include_parameters=False):
    lines = []
    related_tables = RELATED_TABLES
    for table_name in SYSTEM_TABLES[::-1]:
        if not include_parameters and table_name == 'parameter_parameters':
            continue
        if table_name in related_tables:
            main_table = table_name
            rel_table = related_tables[table_name][0]
            rel_field = related_tables[table_name][1]
            lines.append(f"DELETE FROM {main_table} WHERE {rel_field} in (select id from {rel_table} where sys_id={sys_id});")
            continue
        if table_name == 'system_systemorg_permissions':
            lines.append(f"DELETE FROM {table_name} WHERE systemorg_id in (select id from system_systemorg where sys_id={sys_id});")
            continue
        lines.append(f"DELETE FROM {table_name} WHERE sys_id={sys_id};")
    return "\n".join(lines)


def export_define_sql(sys_id, org_id=None):
    insert_sql_lines = []
    for table_name in DEFINE_TABLES:
        try:
            insert_sql_lines.append(export_sql_insert(table_name, sys_id, None))
        except Exception as e:
            print(table_name)
            raise e
    return "\n".join(insert_sql_lines)


def export_cms_sql(sys_id):
    insert_sql_lines = []
    for table_name in CMS_TABLES:
        try:
            insert_sql_lines.append(export_sql_insert(table_name, sys_id))
        except Exception as e:
            print(table_name)
            raise e
    return "\n".join(insert_sql_lines)


def export_data_sql(sys_id, org_id):
    insert_sql_lines = []
    for table_name in DATA_TABLES:
        if table_name in IGNORE_EXPORT_TABLES:
            continue
        try:
            insert_sql_lines.append(export_sql_insert(table_name, sys_id, org_id))
        except Exception as e:
            print(table_name)
            raise e
    return "\n".join(insert_sql_lines)


def export_delete_sql(sys_id, org_id=None, include_cms=False, include_define=False, include_parameters=False):
    """导出删除语句，根据sys_id和org_id拼装where条件"""
    related_tables = RELATED_TABLES
    if org_id is not None:
        sql_tmpl = "DELETE FROM {table_name} WHERE sys_id={sys_id} AND org_id={org_id};"
        sql_rel_tmpl = "DELETE FROM {table_name} WHERE {rel_field} in (select id from {rel_table} where sys_id={sys_id} AND org_id={org_id});"
        format_kwargs = {"sys_id": sys_id, "org_id": org_id, "table_name": ""}
    else:
        sql_tmpl = "DELETE FROM {table_name} WHERE sys_id={sys_id};"
        sql_rel_tmpl = "DELETE FROM {table_name} WHERE {rel_field} in (select id from {rel_table} where sys_id={sys_id});"
        format_kwargs = {"sys_id": sys_id, "table_name": ""}
    delete_sql_lines = []
    # 附加清空表外加业务表数据表
    for table_name in DEL_DATA_TABLES + DATA_TABLES[::-1]:
        format_kwargs['table_name'] = table_name
        if include_define and table_name in related_tables:
            format_kwargs['rel_table'] = related_tables[table_name][0]
            format_kwargs['rel_field'] = related_tables[table_name][1]
            delete_sql_lines.append(sql_rel_tmpl.format(**format_kwargs))
            continue
        delete_sql_lines.append(sql_tmpl.format(**format_kwargs))
    if include_define and org_id is not None:
        delete_sql_lines.append(
            f"DELETE FROM workflow_workflowrole_users WHERE workflowrole_id in (select id from workflow_workflowrole where sys_id={sys_id} and org_id={org_id});"
        )
        for table_name in DEFINE_TABLES[::-1]:
            format_kwargs['table_name'] = table_name
            if table_name in related_tables:
                format_kwargs['rel_table'] = related_tables[table_name][0]
                format_kwargs['rel_field'] = related_tables[table_name][1]
                delete_sql_lines.append(sql_rel_tmpl.format(**format_kwargs))
                continue
            delete_sql_lines.append(sql_tmpl.format(**format_kwargs))
    if include_cms:
        for table_name in CMS_TABLES[::-1]:
            format_kwargs['table_name'] = table_name
            delete_sql_lines.append(sql_tmpl.format(**format_kwargs))
    if org_id is None:
        delete_sql_lines.append(export_system_del_sql(sys_id, include_parameters))
    return "\n".join(delete_sql_lines)


def export_sys_sql(
    sys_id, org_id=None,
    include_cms=False,
    include_data=False,
    include_delete=False,
    include_parameters=False
):
    insert_sql_lines = []
    insert_sql_lines.append(SQL_HEAD)
    if include_delete:
        insert_sql_lines.append("-- delete start\n\n")
        insert_sql_lines.append(export_delete_sql(sys_id, org_id, include_cms, True, include_parameters=include_parameters))
        insert_sql_lines.append("-- delete end\n\n")
    insert_sql_lines.append("-- insert start\n\n")
    if org_id is None:
        insert_sql_lines.append(export_system_sql(sys_id, include_parameters=include_parameters))
    insert_sql_lines.append(export_define_sql(sys_id, org_id))
    if include_cms:
        insert_sql_lines.append(export_cms_sql(sys_id))
    if include_data:
        insert_sql_lines.append(export_data_sql(sys_id, org_id))
    return "\n".join(insert_sql_lines)
