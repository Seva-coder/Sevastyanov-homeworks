from django.core.exceptions import ValidationError
from django import forms


class EditForm(forms.Form):
    title = forms.CharField(max_length=50, label='Заголовок:')
    state = forms.CharField(max_length=11, label='состояние:')
    estimate = forms.DateTimeField(label='новая дата:')

    def clean_state(self):
        value = self.cleaned_data.get('state')
        if value != 'in_progress' and value != 'ready':
            raise ValidationError('поле State приняло нестандартное значение')
        return value
