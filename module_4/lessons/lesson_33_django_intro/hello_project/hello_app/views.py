from django.http import HttpResponse
from django.shortcuts import render

from .models import Note


def index(request):
    return HttpResponse("Hello, Django!")


def about(request):
    return HttpResponse("Це моя перша сторінка на Django!")


def note_list(request):
    notes = Note.objects.all()
    return render(request, "hello_app/note_list.html", {"notes": notes})
