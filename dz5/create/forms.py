import pytz
from django.core.exceptions import ValidationError
from datetime import datetime
from django import forms


class CreateForm(forms.Form):
    title = forms.CharField(max_length=50, label='Имя задачи:')
    date = forms.DateTimeField(label='дата:')

    def clean_date(self):
        value = self.cleaned_data.get('date')
        if value < datetime.now(tz=pytz.timezone('Europe/Moscow')):
            raise ValidationError('back to the future not allowed!')
        return value
