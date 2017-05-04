from django.shortcuts import render
from .forms import CreateForm
from datetime import datetime, timedelta
import pytz

def view_creation(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        info = 'Форма заполнена, но некорректна'
        red = False
        display_result = False
        title = '' #только для IDE, рендериться будет только валидный заголовок
        date = ''
        if form.is_valid():
            display_result = True
            info = 'Форма заполнена и корректна'
            title = form.cleaned_data['title']
            date = form.cleaned_data['date']
            if form.cleaned_data['date'] - datetime.now(tz=pytz.timezone('Europe/Moscow')) < timedelta(days=3):
                red = True
    else:
        title = '' #только для IDE, рендериться всё равно не будет
        date = ''
        red = False
        display_result = False
        info = 'Форма не заполнена'
        form = CreateForm(initial={'title': 'какая-то задача'})

    return render(
        request, 'creation.html',
        {'form': form, 'info': info, 'red_title': red, 'display': display_result, 'task_title': title, 'date': date}
    )
