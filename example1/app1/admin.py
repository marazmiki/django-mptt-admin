# coding: utf-8

from django.contrib import admin
from app1.models import Category
from mpttadmin import MpttAdmin

class CategoryAdmin(MpttAdmin):
    tree_title_field = 'name'
    tree_display = ('name','slug','created|date')
    prepopulated_fields = {"slug": ("name",)}

    class Meta:
        model = Category


admin.site.register(Category, CategoryAdmin)


