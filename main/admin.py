from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from main.models import Client, CarType, EngineType, CarAccessory, Car, Rent


class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    verbose_name_plural = 'client'


class UserAdmin(UserAdmin):
    inlines = (ClientInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(CarType)
admin.site.register(EngineType)
admin.site.register(CarAccessory)
admin.site.register(Car)
admin.site.register(Rent)
