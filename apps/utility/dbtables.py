"""
数据导出功能数据表定义
"""

# 系统表，不区分org_id
SYSTEM_TABLES = [
    'usercenter_funcpermission',
    'system_system',
    'system_system_default_org_permissions',
    'system_systembiz',
    'system_systemorg',
    'system_systemorg_permissions',
    'system_systemproject',
    'system_systemprojectrouter',
    'system_systemprojectmenu',
    'system_wechatconfig',
    'system_smsconfig',
    'system_emailconfig',
    'parameter_parameters',
    # 'coderegister_codemodule',
]

# 定义表，不区分org_id
DEFINE_TABLES = [
    'formtemplate_formdatareportconf',
    'formtemplate_formtemplate',
    'formtemplate_formfields',
]

# CMS表，不区分org_id
CMS_TABLES = [
]

# 业务表数据表，区分org_id
DATA_TABLES = [
    'baseconfig_basetree',
    'usercenter_funcgroup',
    'usercenter_funcgroup_permissions',
    'usercenter_department',
    'usercenter_user',
    'usercenter_department_dep_manager',
    'usercenter_user_category',
    'usercenter_user_func_groups',
    'usercenter_user_func_user_permissions',
    'goods_goods',
    'org_org',
    'service_services',
    'formtemplate_formdata',
    'customer_customer',
]

# 附加清空表，在有删除操作时，需要清空的表
DEL_DATA_TABLES = [
    'formtemplate_formdatareportconf',
    'formtemplate_formaggrgatefields',
    'formtemplate_formtemplate',
    'formtemplate_formfields',
]

RELATED_TABLES = {
    'system_systemproject': ['system_system', 'system_id'],
    'system_system_default_org_permissions': ['system_system', 'system_id'],
    'system_wechatconfig': ['system_system', 'system_id'],
    'system_smsconfig': ['system_system', 'system_id'],
    'system_systemorg_permissions': ['system_systemorg', 'systemorg_id'],
    'usercenter_user_func_user_permissions': ['usercenter_user', 'user_id'],
    'usercenter_user_func_groups': ['usercenter_user', 'user_id'],
    'usercenter_user_category': ['baseconfig_basetree', 'basetree_id'],
    'usercenter_department_dep_manager': ['usercenter_user', 'user_id'],
    'usercenter_funcgroup_permissions': ['usercenter_funcpermission', 'funcpermission_id'],
    'formtemplate_formaggrgatefields': ['formtemplate_formtemplate', 'template_id'],
    'formtemplate_formfields': ['formtemplate_formtemplate', 'template_id'],
    'formtemplate_formtemplate': ['usercenter_user', 'creator_id'],
    'formtemplate_formdatareportconf': ['usercenter_funcpermission', 'permission_id'],
}

IGNORE_EXPORT_TABLES = [

]
