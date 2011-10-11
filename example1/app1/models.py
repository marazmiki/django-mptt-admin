# coding: utf-8
from django.db import models
import mptt

class Category(models.Model):
    parent = models.ForeignKey('self', verbose_name='Parent category', null=True, blank=True, related_name='children')
    name = models.CharField('Name', max_length=255)
    slug = models.SlugField('Slug', max_length=100, blank=True, unique=True)
    created = models.DateTimeField('Created', auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = u'Categories'
        
mptt.register(Category)

