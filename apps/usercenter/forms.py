from django import forms

from . import models


class PhoneAccessForm(forms.Form):
    phone = forms.CharField(label='手机号码', max_length=30, help_text='手机号码')
    phone_access = forms.CharField(label='验证码', max_length=10, help_text='验证码')

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        phone_access = cleaned_data.get("phone_access")
        pa = models.PhoneAccess.objects.filter(phone=phone, phone_access=phone_access)
        if not pa:
            raise forms.ValidationError('验证码错误')
        return cleaned_data
