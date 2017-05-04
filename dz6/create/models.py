from django.db import models

class Roadmap(models.Model):
    roadmap_name = models.CharField(max_length=50, verbose_name='Название Roadmap:')

class Task(models.Model):
    roadmap = models.ForeignKey('Roadmap', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, verbose_name='Название задачи:')
    state = models.CharField(max_length=11, verbose_name='статус:')
    estimate = models.DateTimeField(verbose_name='Срок выполнения')
