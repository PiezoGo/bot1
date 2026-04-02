from django.shortcuts import render
from django.views.generic import TemplateView
from openai import OpenAI

# Create your views here.

client = OpenAI

class HomePageView(TemplateView):
    template_name = 'index.html'

