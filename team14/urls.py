from django.urls import path
from . import views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path('reading/training-levels/', views.training_levels, name='training_levels'),
    path('easy/', views.easy_level, name='easy_level'),
    path('medium/', views.mid_level, name='mid_level'),
    path('hard/', views.hard_level, name='hard_level'),
    path('Exam/', views.Exam_Page, name='Exam_Page'),

]