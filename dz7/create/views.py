import time
import math
from decimal import *
from datetime import datetime
from django.shortcuts import render, redirect
from django.db.models import Max, ExpressionWrapper, DurationField, F, Sum
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
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
        if form.is_valid():
            task = form.save(commit=False)
            task.roadmap = Roadmap.objects.get(pk=int(form.cleaned_data['roadmap']))
            task.creation_date = timezone.now()
            task.user = request.user
            task.save()
            score = Scores(task=task)
            score.save()
            messages.add_message(request, messages.INFO, 'Задача добавлена')
            return redirect('all_tasks')
        else:
            messages.add_message(request, messages.WARNING, 'В форме что-то не так')
            new_form = CreateTask(request.POST, choices=variants, initial={'title': request.POST['title']})
            return render(
                request, 'create_task.html',
                {'form': new_form}
            )
    else:
        if len(variants) == 0:
            messages.add_message(request, messages.WARNING, 'Нет Roadmaps, надо сначала создать их')
            return render(
                request, 'create_task.html',
            )  # не выдаём форму, шаблон на её место подставит ссылку н асоздание Roadmap
        else:
            form = CreateTask(choices=variants)
            return render(
                request, 'create_task.html',
                {'form': form}
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
    elif Task.objects.filter(pk=id_task).exists() and Task.objects.get(pk=id_task).user == request.user:  # удалить только свои Task
        Task.objects.get(pk=id_task).delete()
        messages.add_message(request, messages.INFO, 'Задача удалена')
    else:
        raise PermissionDenied
    return redirect('all_tasks')


@login_required
def edit_task(request, id_task=-1):  # '-1' переназначится из ссылки по которой вызвали
    if request.method == 'POST':
        form = EditTask(request.POST, user=request.user)
        if form.is_valid():
            id_task = form.cleaned_data['id_task']
            if int(id_task) > MAX_ID:
                raise PermissionDenied
            elif Task.objects.filter(pk=id_task).exists() and Task.objects.get(pk=id_task).user == request.user:
                old_task = Task.objects.get(pk=id_task)
                old_state = old_task.state
                old_estimate = old_task.estimate
                task = old_task
                form = EditTask(request.POST, instance=task, user=request.user)
                task = form.save(commit=False)
                task.roadmap = Roadmap.objects.get(pk=form.cleaned_data['roadmap'])
                task.save()
                if form.cleaned_data['state'] != old_state:
                    if form.cleaned_data['state'] is True and old_state is False:
                        today = timezone.now()
                        creation_date = task.creation_date
                        abc = Task.objects.annotate(
                            delta=ExpressionWrapper(
                                F('estimate')-F('creation_date'), output_field=DurationField()
                            )
                        )
                        max_estimate = abc.aggregate(Max('delta'))
                        scores = (today-creation_date)/(old_estimate-creation_date) + \
                                 (old_estimate-creation_date)/(max_estimate['delta__max'])
                        getcontext().prec = 6  # 6 цифр для Decimal, как в бд
                        if Decimal(scores) > Decimal(999.999):   # превышшение max значеня БД
                            Scores.objects.filter(task=task).update(points=Decimal(999.999))
                        elif Decimal(scores) < Decimal(-999.999):   # превышшение max/min значеня БД
                            Scores.objects.filter(task=task).update(points=Decimal(-999.999))
                        else:
                            Scores.objects.filter(task=task).update(points=Decimal(scores))
                        Scores.objects.filter(task=task).update(date=today)
                messages.add_message(request, messages.INFO, 'Задача отредактирована')
                return redirect('all_tasks')
            else:
                raise PermissionDenied
        else:
            messages.add_message(request, messages.WARNING, 'В форме ошибка')
            new_form = EditTask(initial={'title': request.POST['title'], 'state': request.POST.get('state', False),
                                         'estimate': request.POST['estimate'], 'id_task': request.POST['id_task']},
                                user=request.user)
            return render(
                request, 'edit_task.html',
                {'form': new_form}
            )
    else:
        if int(id_task) < MAX_ID and Task.objects.filter(pk=id_task).exists() and \
                        Task.objects.get(pk=id_task).user == request.user:
            current_task = Task.objects.get(pk=id_task)
            form = EditTask(initial={'title': current_task.title, 'state': current_task.state,
                                     'estimate': current_task.estimate, 'id_task': id_task}, user=request.user)
            return render(
                request, 'edit_task.html',
                {'form': form}
            )
        else:
            raise PermissionDenied


@login_required
def statistic_all(request):
    stats = []
    for week in range(0, 53):
        start_time = time.strftime('%Y-%m-%d', time.strptime('1-'+str(week)+'-2017', '%w-%W-%Y'))  # надо допилить для автоматического года
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
    )  # range здесь - тк в шаблонах они не работают


def create_user(request):
    if request.method == 'POST':
        form = CreateNewUser(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Аккаунт создан')
            user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('acc_view')
        else:
            messages.add_message(request, messages.WARNING, 'Ошибка в форме')
            if TaskUser.objects.filter(email=request.POST.get('email')).exists():
                messages.add_message(request, messages.WARNING, 'Такой e-mail уже занят')
            new_form = CreateNewUser(initial={'email': request.POST['email'], 'last_name': request.POST['last_name'],
                                              'first_name': request.POST['first_name'], 'age': request.POST['age'],
                                              'region': request.POST['region'], 'phone': request.POST['phone']})
            return render(
                request, 'regform.html',
                {'form': new_form}
            )
    else:
        form = CreateNewUser()
        return render(
            request, 'regform.html',
            {'form': form}
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
            messages.add_message(request, messages.INFO, 'Профиль отредактирован')
            return redirect('acc_view')
        else:
            messages.add_message(request, messages.WARNING, 'В форме были ошибки')  # не знаю какие, но на всякий случай
            return render(
                request, 'acc_edit.html',
                {'form': form}
            )
    else:
        data = TaskUser.objects.get(pk=request.user)
        form = EditUser(initial={'first_name': data.first_name, 'last_name': data.last_name,
                                 'phone': data.phone, 'age': data.age, 'region': data.region})
        return render(
            request, 'acc_edit.html',
            {'form': form}
        )
