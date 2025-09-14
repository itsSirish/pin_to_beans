
# Register your models here.
from django.contrib import admin
from .models import Image, User, Pin, Pinboard

admin.site.register(Image)
admin.site.register(User)
admin.site.register(Pin)
admin.site.register(Pinboard)
