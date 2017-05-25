from django.core.exceptions import ValidationError
from django import forms
from .models import Task, Roadmap, TaskUser
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib import messages

class CreateTask(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'state', 'estimate']
        exclude = ['creation_date']

    def __init__(self, *args, **kwargs):  # шайтан-код для автоматического обновления select'a на форме
        self.choices = kwargs.pop('choices')
        super().__init__(*args, **kwargs)
        self.fields['roadmap'].choices = self.choices
        self.fields['roadmap'].widget.attrs.update({'class': 'form-control'})

    roadmap = forms.ChoiceField(widget=forms.Select, label='Roadmap?')

    def clean_estimate(self):
        value = self.cleaned_data.get('estimate')
        if value < timezone.now():
            raise ValidationError('back to the future not allowed!')
        return value


class CreateRoadmap(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')   # для предотвращения создания Raoadmap с одинаковыми именами ОДНИМ юзером
        super(CreateRoadmap, self).__init__(*args, **kwargs)

    class Meta:
        model = Roadmap
        fields = ['roadmap_name']

    def clean_roadmap_name(self):
        value = self.cleaned_data.get('roadmap_name')
        if Roadmap.objects.filter(roadmap_name=value, user=self.user).exists():
            raise ValidationError('такой Roadmap уже существует!')
        return value


class EditTask(CreateTask):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # для выдачи юзеру только его Roadmap's в выпадающем списке
        kwargs['choices'] = [(road.id, road.roadmap_name) for road in Roadmap.objects.filter(user=self.user)]
        super().__init__(*args, **kwargs)
    id_task = forms.IntegerField(widget=forms.HiddenInput())

    def clean_estimate(self):  # чтобы можно было испралять state после того как срок прошёл
        value = self.cleaned_data.get('estimate')
        return value


class CreateNewUser(UserCreationForm):
    class Meta:
        model = TaskUser
        fields = ['email', 'phone', 'first_name', 'last_name', 'age', 'region']


class EditUser(forms.ModelForm):  # а как унаследоваться от CreateNewUser без полей и проверки паролей?
    class Meta:
        model = TaskUser
        exclude = ['email', 'password', 'last_login', 'is_superuser', 'groups', 'user_permissions', 'is_staff',
                   'is_active', 'date_joined', 'username']
