from django.contrib import admin
from .models import UserProfile, Folder, Task, AdminMessage, MotivationalQuote

admin.site.register(UserProfile)
admin.site.register(Folder)
admin.site.register(Task)
admin.site.register(AdminMessage)
admin.site.register(MotivationalQuote)
