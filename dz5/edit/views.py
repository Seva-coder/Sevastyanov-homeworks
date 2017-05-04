from django.shortcuts import render
from .forms import EditForm

# Create your views here.
def edition(request):
    if request.method == 'POST':
        form = EditForm(request.POST)
        info = 'Форма заполнена, но некорректна'
        if form.is_valid():
            info = 'Форма заполнена и корректна'
    else:
        info = 'Форма не заполнена'
        form = EditForm(initial={'title': 'редактирование задачи'})
    return render(
        request, 'edition.html',
        {'form': form, 'info': info}
    )
