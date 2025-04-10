from django.apps import AppConfig


class UsercenterConfig(AppConfig):
    name = 'usercenter'
    verbose_name = '01.机构和用户管理'

    def ready(self):
        import usercenter.signal_handlers
