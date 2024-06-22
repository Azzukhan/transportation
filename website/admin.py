from django.contrib import admin
from .models import Company, Trip, Invoice

admin.site.register(Company)
admin.site.register(Trip)
admin.site.register(Invoice)
