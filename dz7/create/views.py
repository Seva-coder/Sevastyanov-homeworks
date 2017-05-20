import time
import math
from decimal import *
from datetime import datetime
from django.shortcuts import render, redirect
from django.db.models import Max, ExpressionWrapper, DurationField, F, Sum
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CreateRoadmap, CreateTask, EditTask, CreateNewUser, EditUser
from .models import Roadmap, Task, Scores, TaskUser



MAX_ID = math.pow(2, 32)  # ограничение бд на int, чтобы из delete не вылезти за диапазон

@login_required
def create_roadmap(request):
    if request.method == 'POST':
        form = CreateRoadmap(request.POST,  user=request.user)
        info = 'Форма заполнена, но некорректна'
        if form.is_valid():
            road = form.save(commit=False)
            road.user = request.user
            road.save()
            info = 'Roadmap сохранён'
    else:
        info = 'Форма не заполнена'
        form = CreateRoadmap(initial={'roadmap_name': 'название сборника задач'}, user=request.user)
    return render(
        request, 'create_roadmap.html',
        {'form': form, 'info': info}
    )


@login_required
def all_roadmaps(request):
    roads = Roadmap.objects.filter(user=request.user)
    return render(
        request, 'allroadmaps.html',
        {'tasks': roads}
    )

@login_required
def delete_roadmap(request, id_road):
    if int(id_road) > MAX_ID:
        raise PermissionDenied
    elif Roadmap.objects.filter(pk=id_road).exists() and Roadmap.objects.get(pk=id_road).user == request.user:
        Roadmap.objects.get(pk=id_road).delete()
    else:
        raise PermissionDenied
    return redirect('all_roadmap')


@login_required
def create_task(request):
    variants = [(road.id, road.roadmap_name) for road in Roadmap.objects.filter(user=request.user)]
    if request.method == 'POST':
        form = CreateTask(request.POST, choices=variants)
        info = 'Форма невалидна'
        if form.is_valid():
            info = 'задача сохранена'
            #roadmap_id = int(form.cleaned_data['roadmap'])
            #title = form.cleaned_data['title']
            #state = form.cleaned_data['state']
            #estimate = form.cleaned_data['estimate']
            #creation_date = timezone.now() # datetime.now(tz=pytz.timezone('Europe/Moscow'))
            #road = Roadmap.objects.get(pk=roadmap_id)
            #tsk = road.task_set.create(
            #    title=title,
            #    state=state,
            #    estimate=estimate,
            #    creation_date=creation_date,
            #    user=request.user
            #)  #автоматический save
            task = form.save(commit=False)
            task.roadmap = Roadmap.objects.get(pk=int(form.cleaned_data['roadmap']))
            task.creation_date = timezone.now()
            task.user = request.user
            task.save()
            score = Scores(task=task)
            score.save()
    else:
        if len(variants) == 0:
            info = "'Roadmap'ов нет, добавьте сначала их"
            return render(
            request, 'create_task.html',
            {'info': info}
            )
        else:
            form = CreateTask(choices=variants)
            info = 'необходимо заполнить все поля'
    return render(
        request, 'create_task.html',
        {'form': form, 'info': info}
    )


@login_required
def all_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    return render(
        request, 'alltasks.html',
        {'tasks': tasks.order_by('state', 'estimate')}
    )

@login_required
def delete_task(request, id_task):
    if int(id_task) > MAX_ID:
        raise PermissionDenied
    elif Task.objects.filter(pk=id_task).exists() and Task.objects.get(pk=id_task).user == request.user: # удалить только свои Task
        Task.objects.get(pk=id_task).delete()
    else:
        raise PermissionDenied
    return redirect('all_tasks')


@login_required
def edit_task(request, id_task=-1):  # '-1' переназначится из ссылки по которой вызвали
    if request.method == 'POST':
        info = 'Форма невалидна'
        form = EditTask(request.POST, user=request.user)
        if form.is_valid():
            id_task = form.cleaned_data['id_task']
            if int(id_task) > MAX_ID:
                raise PermissionDenied
            elif Task.objects.filter(pk=id_task).exists() and Task.objects.get(pk=id_task).user == request.user:
                old_task = Task.objects.get(pk=id_task)
                old_state =  old_task.state
                old_estimate = old_task.estimate
                task = old_task
                form = EditTask(request.POST, instance=task, user=request.user)
                task = form.save(commit=False)
                task.roadmap = Roadmap.objects.get(pk=form.cleaned_data['roadmap'])
                task.save()
                if form.cleaned_data['state'] != old_state:
                    if form.cleaned_data['state'] == True and old_state == False:
                        today = timezone.now() # datetime.now(tz=pytz.timezone('Europe/Moscow'))
                        creation_date = task.creation_date
                        abc = Task.objects.annotate(
                            delta=ExpressionWrapper(
                                F('estimate')-F('creation_date'), output_field=DurationField()
                            )
                        )
                        max_estimate = abc.aggregate(Max('delta'))
                        scores = (today-creation_date)/(old_estimate-creation_date) + (old_estimate-creation_date)/(max_estimate['delta__max'])
                        getcontext().prec = 6  # 6 цифр для Decimal, как в бд
                        if Decimal(scores) > Decimal(999.999):   # превышшение max значеня БД
                            Scores.objects.filter(task=task).update(points=Decimal(999.999))
                        else:
                            Scores.objects.filter(task=task).update(points=Decimal(scores))
                        Scores.objects.filter(task=task).update(date=today)
                info = 'Изменения применены, ну по идее...'
            else:
                raise PermissionDenied
    else:
        current_task = Task.objects.get(pk=id_task)
        form = EditTask(initial={'title': current_task.title, 'state': current_task.state, 'estimate': current_task.estimate, 'id_task': id_task}, user=request.user)
        info = ''
    return render(
        request, 'edit_task.html',
        {'form': form, 'info': info}
    )


@login_required
def statistic_all(request):
    stats = []
    for week in range(0, 53):
        start_time = time.strftime('%Y-%m-%d', time.strptime('1-'+str(week)+'-2017', '%w-%W-%Y')) # надо допилить для автоматического года
        stop_time = time.strftime('%Y-%m-%d', time.strptime('0-'+str(week)+'-2017', '%w-%W-%Y'))
        created = Task.objects.filter(
            user=request.user,
            creation_date__date__gte=datetime.strptime(start_time, "%Y-%m-%d"),
            creation_date__date__lte=datetime.strptime(stop_time, "%Y-%m-%d")  # не __week так 1 января - 53 неделя
            ).count()
        solved = Scores.objects.filter(
            task__user=request.user,
            date__date__gte=datetime.strptime(start_time, "%Y-%m-%d"),
            date__date__lte=datetime.strptime(stop_time, "%Y-%m-%d")
            ).count()
        if created != 0 or solved != 0:
            stats.append([week, start_time + ' / ' + stop_time, created, solved])
    score = []
    for month in range(1, 13):
        points = Scores.objects.filter(task__user=request.user, date__month=month).aggregate(Sum('points'))['points__sum']
        if points is not None and points != 0:
            score.append(['2017-'+str(month), points])
    return render(
        request, 'statistics_all.html',
        {'info': stats, 'range': range(4), 'score': score, 'range2': range(2)}
    )  #  range здесь - тк в шаблонах они не работают


def create_user(request):
    if request.method == 'POST':
        form = CreateNewUser(request.POST)
        info = 'что-то невалидно'
        if form.is_valid():
            info = 'всё ОК, новый акк создан'
            form.save()
    else:
        form = CreateNewUser()
        info = 'надо бы заполнить'
    return render(
        request, 'regform.html',
        {'form': form, 'info': info}
    )


@login_required
def view_user(request):
    return render(
        request, 'acc_view.html'
    )


@login_required
def edit_user(request):
    if request.method == 'POST':
        man = TaskUser.objects.get(pk=request.user)
        form = EditUser(request.POST, instance=man)
        if form.is_valid():
            form.save()
            return redirect('acc_view')
        else:
            return render(
                request, 'base.html',
                {'form': form}
            )
    else:
        data = TaskUser.objects.get(pk=request.user)
        form = EditUser(initial={'first_name': data.first_name, 'last_name': data.last_name, 'phone': data.phone, 'age': data.age, 'region': data.region})
        return render(
            request, 'acc_edit.html',
            {'form': form}
        )







