from django.contrib import admin
from .models import Address, Status


# Register your models here.
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'created_at']
    search_fields = ['case_number']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'status', 'created_at']
