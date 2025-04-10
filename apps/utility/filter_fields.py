import django_filters
from django import forms
from django_filters.fields import ChoiceIteratorMixin, ChoiceIterator, BaseCSVField, BaseCSVWidget


class NoValidFormMultipleChoiceField(forms.MultipleChoiceField):

    def valid_value(self, value):
        return True


class NoValidMultipleChoiceField(ChoiceIteratorMixin, NoValidFormMultipleChoiceField):
    iterator = ChoiceIterator

    def __init__(self, *args, **kwargs):
        self.empty_label = None
        super().__init__(*args, **kwargs)


# 不检查值是否存在的多选过滤字段 like MultipleChoiceFilter
class NoValidMultipleChoiceFilter(django_filters.MultipleChoiceFilter):
    """不检查值是否存在的多选过滤字段 like MultipleChoiceFilter"""
    field_class = NoValidMultipleChoiceField


class MyBaseCSVField(BaseCSVField):
    base_widget_class = BaseCSVWidget

    def clean(self, value):
        attr = super().clean(value)
        if isinstance(attr, list):
            attr.append(",".join(value))
        return attr


# 字符串多选（in 查询）
class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """字符串多选（in 查询）"""

    base_field_class = MyBaseCSVField

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', '多个值可以用逗号分隔')
        super().__init__(*args, **kwargs)


# 数值多选（in 查询）
class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """数值多选（in 查询）"""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', '多个值可以用逗号分隔')
        super().__init__(*args, **kwargs)

