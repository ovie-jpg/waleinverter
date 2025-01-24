from django.contrib import admin
from .models import Product, Permissions, Profit, Permission, Cart2, CallMeBot, Alertmail

# Register your models here.

admin.site.register(Product)
admin.site.register(Permissions)
admin.site.register(Profit)
admin.site.register(Permission)
admin.site.register(Cart2)
admin.site.register(CallMeBot)
admin.site.register(Alertmail)