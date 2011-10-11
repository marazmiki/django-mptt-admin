# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4
#from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.conf.urls.defaults import *
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import  get_object_or_404
import os
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils import simplejson
from django import template
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt

class MpttAdmin(admin.ModelAdmin):

    def __init__(self,*args,**kargs):
        super(MpttAdmin,self).__init__(*args,**kargs)
        if not hasattr(self,'tree_display'):
            self.tree_display = ()
        if self.tree_display and not hasattr(self,'tree_title_field'):
            self.tree_title_field = self.tree_display[0]
        if not hasattr(self,'tree_title_field'):
            title_field = ''#self.tree_display[0]
        else:
            title_field = '.'+self.tree_title_field
        extra_fields = '&nbsp;'.join('<span title="%s">{{ node.%s }}</span>' % (field,field) for field in self.tree_display if not hasattr(self,'tree_title_field') or field!=self.tree_title_field)
        model = '%s.%s' % (self.Meta.model._meta.app_label, self.Meta.model._meta.object_name)
        self._tree_tpl = template.Template("""{% load mptt_tags %}{% full_tree_for_model """+model+""" as nodes %}{% for node,structure in nodes|tree_info %}{% if structure.new_level %}{% if node.is_child_node %}<ul>{% endif %}<li id="n{{node.pk}}">{% else %}</li><li id="n{{node.pk}}">{% endif %}<ins> </ins><a href="{{node.pk}}/">{{ node"""+title_field+""" }}</a>"""+extra_fields+"""{% for level in structure.closed_levels %}</li>{% if node.is_child_node %}</ul>{% endif %}{% endfor %}{% endfor %}""")
        self._node_tpl = template.Template("""{% for node in nodes %}<li{% if node.is_leaf_node %}{% else %} class="closed"{% endif %} id="n{{node.pk}}"><ins> </ins><a href="{{node.pk}}/">{{ node"""+title_field+""" }}</a>"""+extra_fields+"""</li>{% endfor %}""")
        self._changelist_tpl = template.Template("""{% extends "admin/change_list.html" %}
        {% load mptt_tags %}        
        {% block extrahead %}
        <script src="media/js/lib/jquery-1.3.2.min.js"></script>
        <script src="media/js/lib/jquery.tree.min.js"></script>
        <script src="media/js/lib/plugins/jquery.tree.contextmenu.js"></script>
        <script>var permissions={{permissions|safe}};var parent_attr='{{parent_attr}}';</script>
        <script src="media/js/jstree_admin.js"></script>
        {% endblock %}
        {% block search %}{% endblock %}{% block date_hierarchy %}{% endblock %}
        {% block result_list %}{% endblock %}{% block pagination %}{% endblock %}
        {% block filters %}<div id="tree"><ul>{{tree}}</ul></div>{% endblock %}""")

        #self.move_node = permission_required('%s.change_%s' % (self.model._meta.app_label,self.model._meta.object_name))(self.move_node)
        #self.rename = permission_required('%s.change_%s' % (self.model._meta.app_label,self.model._meta.object_name))(self.rename)
        #self.remove = permission_required('%s.delete_%s' % (self.model._meta.app_label,self.model._meta.object_name))(self.remove)

    def changelist_view(self, request, extra_context=None):
        model = '%s.%s' % (self.Meta.model._meta.app_label, self.Meta.model._meta.object_name)
        opts = self.model._meta
        app_label = opts.app_label

        media = self.media

        module_name = force_unicode(opts.verbose_name_plural)

        permissions = simplejson.dumps({
            'renameable' : self.has_change_permission(request, None) and hasattr(self,'tree_title_field'),
		    'deletable'	: self.has_delete_permission(request, None),
		    'creatable'	: self.has_add_permission(request),
		    'draggable'	: self.has_change_permission(request, None),
        })
        root = self._node_tpl.render(template.Context({
                'nodes':self.Meta.model.tree.root_nodes()
            }))

        context = {
            'module_name': module_name,
            'title': module_name,
            'is_popup': False,
            'cl': {'opts':{'verbose_name_plural': module_name}},
            'media': media,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
            #'tree':self._tree_tpl.render(template.Context()),
            'tree':root,
            'permissions': permissions,
            'parent_attr': self.Meta.model._meta.parent_attr,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        context_instance.update(context)
        return HttpResponse(self._changelist_tpl.render(context_instance))

    def get_urls(self):
        urls = super(MpttAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^tree/$', self.get_tree),
            (r'^move_node/$', self.move_node),
            (r'^rename/$', self.rename),
            (r'^remove/$', self.remove),
            (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                 {'document_root': os.path.join(os.path.dirname(__file__),'media'), 'show_indexes': True}),
        )
        return my_urls + urls

    @csrf_exempt
    def get_tree(self,request):
        if 'id' in request.POST:
            if int(request.POST['id']):
                node = get_object_or_404(self.Meta.model,pk=request.POST['id'])
                nodes = node.get_children()
            else:
                nodes = self.Meta.model.tree.root_nodes()
            c = template.Context({'nodes':nodes})
            return HttpResponse(self._node_tpl.render(c))
        else:
            return HttpResponse(self._tree_tpl.render(template.Context()))

    @csrf_exempt   
    def move_node(self,request):
        if not self.has_change_permission(request, None):
            raise PermissionDenied
        node = get_object_or_404(self.Meta.model,pk=request.POST.get('node'))
        target = get_object_or_404(self.Meta.model,pk=request.POST.get('target'))
        position = request.POST.get('position')
        if position not in ('left','right','last-child','first-child'):
            return HttpResponseBadRequest('bad position')
        self.Meta.model.tree.move_node(node,target,position)
        return self.get_tree(request)

    @csrf_exempt
    def rename(self,request):
        if not self.has_change_permission(request, None):
            raise PermissionDenied
        node = get_object_or_404(self.Meta.model,pk=request.POST.get('node'))
        setattr(node,self.tree_title_field, request.POST.get('name'))
        node.save()
        return self.get_tree(request)

    @csrf_exempt
    def remove(self,request):
        if not self.has_delete_permission(request, None):
            raise PermissionDenied
        node = get_object_or_404(self.Meta.model,pk=request.POST.get('node'))
        node.delete()
        return self.get_tree(request)


