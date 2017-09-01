from django.contrib import admin
from mainsite.models import *

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'nickname', 'gender', 'birthdate')
admin.site.register(Profile, ProfileAdmin)
