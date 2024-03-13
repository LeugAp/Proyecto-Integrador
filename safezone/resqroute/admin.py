from django.contrib import admin
from . import models

admin.site.register(models.Staff)
admin.site.register(models.Node)
admin.site.register(models.Connection)
admin.site.register(models.Brigade)
admin.site.register(models.FunctionsBrigade)
admin.site.register(models.Map)