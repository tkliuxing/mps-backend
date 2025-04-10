from rest_framework.response import Response
from rest_framework import permissions, filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from . import serializers
from . import models
from . import filters as my_filters


class ParametersViewSet(viewsets.ModelViewSet):
    """常参表"""
    queryset = models.Parameters.objects.order_by('pk')
    serializer_class = serializers.ParametersSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = my_filters.ParametersFilterSet
    search_fields = ('category', 'name',)

    def list(self, request, *args, **kwargs):
        """
        常参表查询
        """
        qs = self.filter_queryset(models.Parameters.objects.root_nodes())
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)


class FlatParametersViewSet(viewsets.ModelViewSet):
    """常参表"""
    queryset = models.Parameters.objects.order_by('pk')
    serializer_class = serializers.FlatParametersSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = my_filters.ParametersFilterSet
    search_fields = ('category', 'name',)


class ParametersCategorysViewSet(viewsets.ReadOnlyModelViewSet):
    """常参表分类列表"""
    queryset = models.Parameters.objects.order_by('category')
    serializer_class = serializers.ParametersCategorysSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        ret_list = list(self.queryset.order_by('category').values('category').distinct())
        return Response(ret_list)


class ParametersToBaseTreeViewSet(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """复制到分类树"""
    queryset = models.Parameters.objects.order_by('category')
    serializer_class = serializers.ParametersToBaseTreeSerializer
    permission_classes = [permissions.IsAuthenticated]
