from django.contrib import admin

# Register your models here.

from create.models import Roadmap, Task

admin.site.register(Roadmap)
admin.site.register(Task)
