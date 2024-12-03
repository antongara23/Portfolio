from django.contrib import admin
from .models import User, Ad, Message, Dialog


admin.site.register(User)
admin.site.register(Ad)
admin.site.register(Dialog)
admin.site.register(Message)
