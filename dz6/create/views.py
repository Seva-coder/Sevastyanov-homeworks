from django.shortcuts import render
from .forms import CreateRoadmap, CreateTask, EditTask
from .models import Roadmap, Task
from datetime import datetime, timedelta
import pytz

def create_roadmap(request):
    if request.method == 'POST':
        form = CreateRoadmap(request.POST)
        info = 'Форма заполнена, но некорректна'
        if form.is_valid():
            info = 'Roadmap сохранён'
            name = form.cleaned_data['roadmap_name']
            ex1 = Roadmap(roadmap_name=name)
            ex1.save()
    else:
        info = 'Форма не заполнена'
        form = CreateRoadmap(initial={'roadmap_name': 'название сборника задач'})
    return render(
        request, 'create_roadmap.html',
        {'form': form, 'info': info}
    )

def all_roadmaps(request):
    roads = Roadmap.objects.all()
    return render(
        request, 'allroadmaps.html',
        {'tasks': roads}
    )

def delete_roadmap(request, id_road):
    name = Roadmap.objects.get(pk=id_road).roadmap_name
    Roadmap.objects.get(pk=id_road).delete()
    return render(
    request, 'delete_some.html',
    {'deleted': name, 'obj': 'Roadmap'}
    )

def create_task(request):
    variants = [(road.id, road.roadmap_name) for road in Roadmap.objects.all()]
    if request.method == 'POST':
        form = CreateTask(request.POST, choices=variants)
        info = 'Форма невалидна'
        if form.is_valid():
            info = 'задача сохранена'
            roadmap_id = int(form.cleaned_data['roadmap'])
            title = form.cleaned_data['title']
            state = form.cleaned_data['state']
            estimate = form.cleaned_data['estimate']
            road = Roadmap.objects.get(pk=roadmap_id)
            tsk = road.task_set.create(
                title=title,
                state=state,
                estimate=estimate
            )  #автоматический save
    else:
        if len(variants) == 0:
            info = "'Roadmap'ов нет, добавьте сначала их"
            return render(
            request, 'create_task.html',
            { 'info': info}
            )
        else:
            form = CreateTask(choices=variants)
            info = 'необходимо заполнить все поля'
    return render(
        request, 'create_task.html',
        {'form': form, 'info': info}
    )

def all_tasks(request):
    tasks = Task.objects.all()
    return render(
        request, 'alltasks.html',
        {'tasks': tasks.order_by('state', 'estimate')}
    )

def delete_task(request, id_task):
    name = Task.objects.get(pk=id_task).title
    Task.objects.get(pk=id_task).delete()
    return render(
    request, 'delete_some.html',
    {'deleted': name, 'obj': 'Задача'}
    )

def edit_task(request, id_task=-1):
    if request.method == 'POST':
        info = 'Форма невалидна'
        form = EditTask(request.POST)
        if form.is_valid():
            old_title = Task.objects.get(pk=form.cleaned_data['id_task']).title
            old_state = Task.objects.get(pk=form.cleaned_data['id_task']).state
            old_estimate = Task.objects.get(pk=form.cleaned_data['id_task']).estimate
            old_road = Task.objects.get(pk=form.cleaned_data['id_task']).roadmap.pk

            changed_task = Task.objects.filter(pk=form.cleaned_data['id_task'])
            if form.cleaned_data['title'] != old_title:
                changed_task.update(title=form.cleaned_data['title'])
            if form.cleaned_data['state'] != old_state:
                changed_task.update(state=form.cleaned_data['state'])
            if form.cleaned_data['estimate'] != old_estimate:
                changed_task.update(estimate=form.cleaned_data['estimate'])
            if form.cleaned_data['roadmap'] != old_road:
                changed_task.update(roadmap=Roadmap.objects.get(pk=form.cleaned_data['roadmap']))

            info = 'Изменения применены, ну по идее...'
    else:
        current_task = Task.objects.get(pk=id_task)
        form = EditTask(initial={'title': current_task.title, 'state': current_task.state, 'estimate': current_task.estimate, 'id_task': id_task})
        info = ''
    return render(
        request, 'edit_task.html',
        {'form': form, 'info': info}
    )
