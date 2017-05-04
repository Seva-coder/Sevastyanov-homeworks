import pytz
from django.core.exceptions import ValidationError
from datetime import datetime
from django import forms
from .models import Task, Roadmap


class CreateTask(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'state', 'estimate']
    def __init__(self, *args, **kwargs):  # шайтан-код для автоматического обновления select'a на форме
        self.choices = kwargs.pop('choices')
        super().__init__(*args, **kwargs)
        self.fields['roadmap'].choices = self.choices
    roadmap = forms.ChoiceField(widget=forms.Select, label='К какому Roadmap относится?')

    def clean_estimate(self):
        value = self.cleaned_data.get('estimate')
        if value < datetime.now(tz=pytz.timezone('Europe/Moscow')):
            raise ValidationError('back to the future not allowed!')
        return value

    def clean_state(self):
        value = self.cleaned_data.get('state')
        if value != 'in_progress' and value != 'ready':
            raise ValidationError('поле State приняло нестандартное значение')
        return value

class CreateRoadmap(forms.ModelForm):
    class Meta:
        model = Roadmap
        fields = ['roadmap_name']

    def clean_roadmap_name(self):
        value = self.cleaned_data.get('roadmap_name')
        if Roadmap.objects.filter(roadmap_name=value).exists():
            raise ValidationError('такой Roadmap уже существует!')
        return value


class EditTask(CreateTask):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [(road.id, road.roadmap_name) for road in Roadmap.objects.all()]
        super().__init__(*args, **kwargs)
    id_task = forms.IntegerField(widget = forms.HiddenInput())
