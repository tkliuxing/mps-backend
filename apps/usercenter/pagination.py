from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class UCPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    page_query_param = 'page'
    page_size = None
    page_query_description = '分页的页码'
    page_size_query_description = '每页返回的结果数'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.page.has_next()),
            ('previous', self.page.has_previous()),
            ('data', data)
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'next': {
                    'type': 'boolean',
                    'nullable': False,
                    'format': 'uri',
                    'example': False
                },
                'previous': {
                    'type': 'boolean',
                    'nullable': False,
                    'format': 'uri',
                    'example': False,
                },
                'results': schema,
            },
        }
