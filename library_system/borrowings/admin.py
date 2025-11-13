from django.contrib import admin
from .models import Borrowing

@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'borrowed_date', 'due_date', 'status')
    list_filter = ('status', 'borrowed_date')
    search_fields = ('book__title', 'user__username')
    readonly_fields = ('borrowed_date',)