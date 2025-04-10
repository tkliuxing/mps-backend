from django.db.models import CharField, BigAutoField
from .id_gen import gen_new_id


class TableNamePKField(CharField):

    def auto_id(self):
        return gen_new_id(self._prefix)

    # def get_db_prep_value(self, value, connection, prepared=False):
    #     if not prepared:
    #         value = self.auto_id()
    #     return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['blank']
        if kwargs.get('default'):
            del kwargs['default']
        del kwargs['max_length']
        if kwargs.get('editable'):
            del kwargs['editable']
        del kwargs['primary_key']
        args = (self._prefix,)
        return name, path, args, kwargs

    def __init__(self, prefix='', *args, **kwargs):
        if len(prefix) > 10:
            raise AttributeError('prefix > 10 !')
        self._prefix = prefix
        args = []
        kwargs['max_length'] = 32
        kwargs['blank'] = True
        kwargs['null'] = False
        kwargs['primary_key'] = True
        # kwargs['editable'] = False
        # kwargs['default'] = self.auto_id
        kwargs['editable'] = kwargs.get('editable', False)
        if kwargs['editable'] is False:
            kwargs['default'] = self.auto_id
        super().__init__(*args, **kwargs)
