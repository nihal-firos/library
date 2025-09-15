from django.contrib import admin
from .models import Book, BorrowRecord

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'is_borrowed')
    search_fields = ('title', 'author', 'genre')

admin.site.register(Book, BookAdmin)
admin.site.register(BorrowRecord)
