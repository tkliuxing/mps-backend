from rest_framework.filters import SearchFilter
from rest_framework.compat import coreapi, coreschema
from django.utils.encoding import force_str


class SearchBackend(SearchFilter):
    search_title = '搜索'
    search_description_prefix = '使用字符串模糊搜索这些字段'

    def get_schema_fields(self, view):
        fields = ", ".join(getattr(view, 'search_fields', []))
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_str(self.search_title),
                    description=force_str(f'{self.search_description_prefix}: {fields}')
                )
            )
        ]

    def get_schema_operation_parameters(self, view):
        fields = ", ".join(getattr(view, 'search_fields', []))
        return [
            {
                'name': self.search_param,
                'required': False,
                'in': 'query',
                'description': force_str(f'{self.search_description_prefix}: {fields}'),
                'schema': {
                    'type': 'string',
                },
            },
        ]
