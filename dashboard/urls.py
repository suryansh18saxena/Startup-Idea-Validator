from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard,name="dashboard"),
    path('userdashboard/',views.userdashboard,name="userdashboard"),
    path('ideas/', views.manage_ideas, name='manage_ideas'),
    path('ideas/edit/<int:idea_id>/', views.edit_ideas, name='edit_ideas'),
    path('ideas/delete/<int:idea_id>/', views.delete_ideas, name='delete_ideas'),
]