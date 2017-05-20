"""scheduler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from create.views import create_roadmap, all_roadmaps, delete_roadmap, create_task, all_tasks, delete_task, edit_task, statistic_all, create_user, view_user, edit_user

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^createRoad/$', create_roadmap, name='create_roadmap'),
    url(r'^viewRoads/$', all_roadmaps, name='all_roadmap'),
    url(r'^deleteRoadmap/(?P<id_road>[0-9]+)$', delete_roadmap, name='killer'),
    url(r'^createTask/$', create_task, name='create_task'),
    url(r'^viewTasks/$', all_tasks, name='all_tasks'),
    url(r'^deleteTask/(?P<id_task>[0-9]+)$', delete_task, name='del_tsk'),
    url(r'^editTask/(?P<id_task>[0-9]+)$', edit_task, name='edit_tsk'),
    url(r'^editTask/$', edit_task, name='edit_tsk'),
    url(r'^statsAll/$', statistic_all, name='stats_all'),
    url(r'^reg/$', create_user, name='reg'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout_view'),
    url(r'^password_change/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    url(r'^password_change/done/$', auth_views.PasswordChangeView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    url(r'^viewUser/$', view_user, name='acc_view'),
    url(r'^editUser/$', edit_user, name='acc_edit'),
]
