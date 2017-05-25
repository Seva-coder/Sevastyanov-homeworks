from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TaskUser(AbstractUser):
    email = models.EmailField(verbose_name='Почта:', unique=True, primary_key=True)
    phone = models.CharField(max_length=10, verbose_name='Телефон:')
    age = models.IntegerField(verbose_name='Возраст:', null=True, blank=True)
    region = models.CharField(max_length=20, verbose_name='Регион:', blank=True, null=True)
    username = models.CharField(max_length=10, verbose_name='Имя которое не нужно:', blank=True, null=True) # не убрать(
    first_name = models.CharField(_('first name'), max_length=30)  # переопределённые поля
    last_name = models.CharField(_('last name'), max_length=150)
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name', 'username'] # 'username'
    USERNAME_FIELD = 'email'


class Roadmap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roadmap_name = models.CharField(max_length=50, verbose_name='Название Roadmap:')


class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roadmap = models.ForeignKey('Roadmap', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, verbose_name='Название задачи:')
    state = models.BooleanField(verbose_name='Задача решена?', default=False)  # models.CharField(max_length=11, verbose_name='статус:')
    estimate = models.DateTimeField(verbose_name='Срок выполнения:')
    creation_date = models.DateTimeField(null=True)


class Scores(models.Model):
    task = models.OneToOneField('Task', on_delete=models.CASCADE, primary_key=True, related_name='scores')
    date = models.DateTimeField(verbose_name='Дата зачисления очков:', null=True)
    points = models.DecimalField(max_digits=6, decimal_places=3, verbose_name='Зачислено очков:', null=True)
