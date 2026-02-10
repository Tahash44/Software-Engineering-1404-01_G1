from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required

TEAM_NAME = "team14"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

def training_levels(request):
    return render(request, 'team14/training_levels.html')


def index(request):
    return render(request, 'team14/index.html')

def easy_level(request):
    return render(request, 'team14/Easy_Level.html')

def mid_level(request):
    return render(request, 'team14/Mid_Level.html')

def hard_level(request):
    return render(request, 'team14/Hard_Level.html')

def Exam_Page(request):
    return render(request, 'team14/Exam_Page.html')


