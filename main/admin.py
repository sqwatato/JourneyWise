from django.contrib import admin
from .models import *
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username")
    filter_horizontal = ("destinations",)
    
    
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("id", "city", "country", "popular")
    filter_horizontal=("booker",)

admin.site.register(User, UserAdmin)
admin.site.register(Destination, DestinationAdmin)
