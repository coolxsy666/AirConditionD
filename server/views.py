from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def slave(request):
    return HttpResponse("slave")


def master(request):
    return HttpResponse("master")


def test(request, op, id):
    if request.method == "POST":
        print("op=" + op + "   id=" + id)
    return HttpResponse("slave")
