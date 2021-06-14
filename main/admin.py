from django.contrib import admin
from .models import ToDoList, Thread
# Register your models here.
admin.site.register(ToDoList)
admin.site.register(Thread)