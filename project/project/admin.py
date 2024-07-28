from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(ExtraIncome)
admin.site.register(Expenses)