# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView
from .models import Noticias
from cambiaahora.historias.models import Historias
from cambiaahora.multimedias.models import *
from cambiaahora.testimonios.models import Testimonios
from cambiaahora.configuracion.models import Configuracion, Informacion
from django.utils import translation

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .serializers import NoticiasSerializer
from rest_framework import viewsets

# Create your views here.
def set_lang(request, lang_code):
    if not lang_code in ['en', 'es']:
        raise Http404

    next = request.GET.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', '/')
    response = HttpResponseRedirect(next)

    if hasattr(request, 'session'):
        request.session['django_language'] = lang_code
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)

    return response

class IndexView(TemplateView):
    template_name = "cambiaahora/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        cur_language = translation.get_language()
        if cur_language == 'en':
            context['ultimas_noticias'] = Noticias.objects.filter(aprobacion=2,idioma=2).order_by('-fecha')[:6]
            context['ultimas_historia'] = Historias.objects.filter(aprobacion=2,idioma=2).order_by('fecha')[:6]
            context['ultimas_testimonios'] = Testimonios.objects.filter(aprobacion=2,idioma=2).order_by('-fecha')[:6]
            context['albunes'] = Fotos.objects.filter(aprobacion=2,idioma=2).order_by('-id')[:1]
            context['audios'] = Audios.objects.filter(aprobacion=2,idioma=2).order_by('-id')[:4]
            #context['videos'] = Videos.objects.filter(aprobacion=2,idioma=2).order_by('id')[:3]
            context['documentales'] = Documentales.objects.filter(aprobacion=2,idioma=2).order_by('-fecha')[:3]
            context['informacion'] = Informacion.objects.filter(idioma=2).order_by('id')[:1]
        else:
            context['ultimas_noticias'] = Noticias.objects.filter(aprobacion=2,idioma=1).order_by('-fecha')[:6]
            context['ultimas_historia'] = Historias.objects.filter(aprobacion=2,idioma=1).order_by('fecha')[:6]
            context['ultimas_testimonios'] = Testimonios.objects.filter(aprobacion=2,idioma=1).order_by('-fecha')[:6]
            context['albunes'] = Fotos.objects.filter(aprobacion=2,idioma=1).order_by('-id')[:1]
            context['audios'] = Audios.objects.filter(aprobacion=2,idioma=1).order_by('-id')[:4]
            #context['videos'] = Videos.objects.filter(aprobacion=2,idioma=1).order_by('id')[:3]
            context['documentales'] = Documentales.objects.filter(aprobacion=2,idioma=1).order_by('-fecha')[:3]
            context['informacion'] = Informacion.objects.filter(id=1, idioma=1)

        context['config'] = Configuracion.objects.all()[:3]
        return context

#Listar las Noticias
class ListNewsView(ListView):
    template_name = "cambiaahora/noticias/noticias_list.html"
    model = Noticias
    #paginate_by = 6

    def get_queryset(self):
        cur_language = translation.get_language()
        if cur_language == 'en':
            queryset = Noticias.objects.filter(aprobacion=2,idioma=2).order_by('-fecha')
        else:
            queryset = Noticias.objects.filter(aprobacion=2,idioma=1).order_by('-fecha')
        return queryset



class DetailNewsView(DetailView):
    template_name = "cambiaahora/noticias/noticias_detail.html"
    model = Noticias

    def get_context_data(self, **kwargs):
        context = super(DetailNewsView, self).get_context_data(**kwargs)
        cur_language = translation.get_language()
        if cur_language == 'en':
            context['noticias_relacionadas'] = Noticias.objects.filter(aprobacion=2, idioma=2, categoria=self.object.categoria).exclude(id=self.object.id).order_by('-fecha')[:3]
        else:
            context['noticias_relacionadas'] = Noticias.objects.filter(aprobacion=2, idioma=1, categoria=self.object.categoria).exclude(id=self.object.id).order_by('-fecha')[:3]
        return context

class ContactView(TemplateView):
    template_name = "cambiaahora/noticias/contactenos.html"

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class NewsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Noticias.objects.all()
    serializer_class = NoticiasSerializer

def listar_noticias_imagen(request, template="cambiaahora/noticias/noticias_list.html"):
    cur_language = translation.get_language()
    if cur_language == 'en':
        object_list = Noticias.objects.filter(aprobacion=2,idioma=2).exclude(foto__exact='').order_by('-fecha')
    else:
        object_list = Noticias.objects.filter(aprobacion=2,idioma=1).exclude(foto__exact='').order_by('-fecha')
    return render(request, template, locals())

def listar_noticias_video(request, template="cambiaahora/noticias/noticias_list.html"):
    cur_language = translation.get_language()
    if cur_language == 'en':
        object_list = Noticias.objects.filter(aprobacion=2,idioma=2).exclude(url__exact='').order_by('-fecha')
    else:
        object_list = Noticias.objects.filter(aprobacion=2,idioma=1).exclude(url__exact='').order_by('-fecha')
    return render(request, template, locals())

def listar_noticias_audio(request, template="cambiaahora/noticias/noticias_list.html"):
    cur_language = translation.get_language()
    if cur_language == 'en':
        object_list = Noticias.objects.filter(aprobacion=2,idioma=2).exclude(noticiasaudios__titulo__exact='').order_by('-fecha')
    else:
        object_list = Noticias.objects.filter(aprobacion=2,idioma=1).exclude(noticiasaudios__titulo__exact='').order_by('-fecha')
    return render(request, template, locals())
