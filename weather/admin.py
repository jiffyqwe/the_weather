from django.contrib import admin

from weather.models import City
from .models import City
# Register your models here.
admin.site.register(City)