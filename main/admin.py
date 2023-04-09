from django.contrib import admin
from .models import *
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username")
    
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("id", "city", "country", "popular")
    
class TripPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "booker")

admin.site.register(User, UserAdmin)
admin.site.register(Destination, DestinationAdmin)
admin.site.register(TripPlan, TripPlanAdmin)
