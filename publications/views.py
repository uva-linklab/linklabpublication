from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from linklabgroup import settings

def index(request):
    context = {
        "bibbase_url": settings.BIBBASE_URL,
    }

    template = loader.get_template("publications/index.html")
    return HttpResponse(template.render(context, request))

def complete(request):
    context = {
        "bibbase_url": settings.BIBBASE_URL,
    }

    template = loader.get_template("publications/complete.html")
    return HttpResponse(template.render(context, request))

def filter_year(request, id):
    context = {
        "bibbase_url": settings.BIBBASE_URL,
        "filter_year":id,
    }

    template = loader.get_template("publications/filter_year.html")
    return HttpResponse(template.render(context, request))

def filter_author(request, str):
    context = {
        "bibbase_url": settings.BIBBASE_URL,
        "filter_author":str,
    }

    template = loader.get_template("publications/filter_author.html")
    return HttpResponse(template.render(context, request))