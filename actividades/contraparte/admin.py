# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import *
from django import forms
from ckeditor.widgets import CKEditorWidget
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from cambiaahora.utils import *

class ResultadoInline(admin.TabularInline):
    model = Resultado
    extra = 1
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # This method will turn all TextFields into giant TextFields
        if isinstance(db_field, models.TextField):
            return forms.CharField(label=u'Descripción', 
                                   widget=forms.Textarea(attrs={'cols': 60, 'rows':4, 'class': 'docx'}))
        return super(ResultadoInline, self).formfield_for_dbfield(db_field, **kwargs)


class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'organizacion', 'inicio', 'finalizacion', 'contacto']
    filter_horizontal = ['municipios']
    inlines = [ResultadoInline, ]
    
    #sobreescribiendo el metodo para filtrar los objetos    
    def queryset(self, request):       
        if request.user.is_superuser or request.user.has_perm('fadcanic.view_programa'):
            return Proyecto.objects.all()
        return Proyecto.objects.filter(organizacion__admin=request.user)

    def get_form(self, request, obj=None, ** kwargs):
        if request.user.is_superuser:        
            form = super(ProyectoAdmin, self).get_form(request, ** kwargs)
        else:
            form = super(ProyectoAdmin, self).get_form(request, ** kwargs)
            form.base_fields['organizacion'].queryset = request.user.organizacion_set.all()            
            #form.base_fields['proyecto'].queryset = request.user.organizacion_set.all()                        
        return form
    

admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Resultado)
admin.site.register(Organizador)

class Precedencia_Participantes_Inline(admin.TabularInline):
    model = Precedencia_Participantes
    extra = 1

class ActividadAdmin(admin.ModelAdmin):
    list_filter = ['resultado__aporta_a', 'organizacion', 'proyecto', 'persona_organiza', 'fecha']
    search_fields = ['nombre_actividad', 'organizacion__nombre_corto', 'persona_organiza__nombre','municipio__nombre']
    list_display = ['nombre_actividad', 'organizacion', 'fecha', 'tipo']
    
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'cols': 50, 'rows':4, 'class': 'docx'})},
        models.TextField: {'widget': CKEditorWidget()},       
    }

    inlines = [Precedencia_Participantes_Inline]
    
    def get_form(self, request, obj=None, ** kwargs):
        if request.user.is_superuser:
            self.exclude = () 
            self.fieldsets = [
                    (None, {'fields': [('organizacion', 'proyecto'), 'tipo', 'persona_organiza', 'comite', 'nombre_actividad','objetivo_actividad','fecha',
                                       'municipio', 'comunidad']}),
                    ('Tipo, tema y ejes de actividad', {'fields': ['tipo_actividad', 'tema_actividad', 'ejes_transversales']}),
                    ('Participantes por sexo', {'fields': [('hombres', 'mujeres'),]}),
                    ('Participantes por edad', {'fields': [('menor_12', 'mayor_12', 'mayor_18', 'mayor_30', 'no_dato'),]}),
                    ('Participantes por identidad étnica', {'fields': [('creole', 'miskito', 'ulwa', 'no_dato1'), 
                                                           ('rama', 'mestizo', 'mayagna', 'garifuna'),
                                                           ('extranjero',)]}),
                    ('Participantes por tipo', {'fields': [('estudiante', 'docente', 'periodista', 'no_dato2'), 
                                                           ('lideres', 'representantes', 'comunitarios')]}),
                    (None, {'fields': ['resultado',]}),
                    ('Evaluacion de hombres', {'fields': [('relevancia', 'efectividad'), ('aprendizaje', 'empoderamiento'), 'participacion']}),
                    ('Evaluacion de mujeres', {'fields': [('relevancia_m', 'efectividad_m'), ('aprendizaje_m', 'empoderamiento_m'), 'participacion_m']}),
                    ('Recursos', {'fields': [('foto1', 'foto2', 'foto3'), 'video', 'comentarios','logros','dificultades','acuerdos']}), 
                    (None, {'fields': ['aprobacion','user']}),                                                 
                ]
        else:
            self.exclude = ('aprobacion',)
            self.fieldsets = [
                    (None, {'fields': [('organizacion', 'proyecto'), 'tipo', 'persona_organiza', 'comite', 'nombre_actividad','objetivo_actividad','fecha',
                                       'municipio', 'comunidad']}),
                    ('Tipo, tema y ejes de actividad', {'fields': ['tipo_actividad', 'tema_actividad', 'ejes_transversales']}),
                    ('Participantes por sexo', {'fields': [('hombres', 'mujeres'),]}),
                    ('Participantes por edad', {'fields': [('menor_12', 'mayor_12', 'mayor_18', 'mayor_30', 'no_dato'),]}),
                    ('Participantes por identidad étnica', {'fields': [('creole', 'miskito', 'ulwa', 'no_dato1'), 
                                                           ('rama', 'mestizo', 'mayagna', 'garifuna'),
                                                           ('extranjero',)]}),
                    ('Participantes por tipo', {'fields': [('estudiante', 'docente', 'periodista', 'no_dato2'), 
                                                           ('lideres', 'representantes', 'comunitarios')]}),
                    (None, {'fields': ['resultado',]}),
                    ('Evaluacion de hombres', {'fields': [('relevancia', 'efectividad'), ('aprendizaje', 'empoderamiento'), 'participacion']}),
                    ('Evaluacion de mujeres', {'fields': [('relevancia_m', 'efectividad_m'), ('aprendizaje_m', 'empoderamiento_m'), 'participacion_m']}),
                    ('Recursos', {'fields': [('foto1', 'foto2', 'foto3'), 'video', 'comentarios','logros','dificultades','acuerdos']}), 
                    (None, {'fields': ['user',]}),                                                 
                ]
            #form.base_fields['organizacion'].queryset = request.user.organizacion_set.all()                      
        return super(ActividadAdmin, self).get_form(request, obj=None, **kwargs)
    
    #sobreescribiendo el metodo para filtrar los objetos    
    def queryset(self, request):       
        if request.user.is_superuser or request.user.has_perm('fadcanic.view_programa'):
            return Actividad.objects.all()
        return Actividad.objects.filter(organizacion__admin=request.user)

    def save_model(self, request, obj, form, change):
        #guarda todos los objectos   
        obj.save()
        #envio de correo
        if not obj.user.is_superuser:
            try:
                subject, from_email, to = 'Nueva Actividad de Cambia ahora', 'noreply@cambiaahora.com', arreglo_mail
                text_content = "Una nueva actividad ha sido enviada, del usuario " + \
                                str(obj.user) + ', ' + \
                                ' Si decia revisarla dar clic al siguiente enlace' + \
                                ' http://www.cambiaahora.com/admin/contraparte/actividad/' + str(obj.id)
                html_content = "Una nueva actividad ha sido enviada, del usuario " + \
                                str(obj.user) + ', ' + \
                                ' Si decia revisarla dar clic al siguiente enlace' + \
                                ' http://www.cambiaahora.com/admin/contraparte/actividad/' + str(obj.id)
                msg = EmailMultiAlternatives(subject, text_content, from_email, arreglo_mail)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except:
                pass

    class Media:
        js = ('/static/actividades/js/actividad.js', )        
    
admin.site.register(Actividad, ActividadAdmin)

class OutputAdmin(admin.ModelAdmin):
    list_display = ['_hash', 'date', 'time']
    
#admin.site.register(Output, OutputAdmin)    
    
    
