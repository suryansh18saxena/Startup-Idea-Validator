from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard,name="dashboard"),
    path('create_idea/',views.create_idea,name="create_idea"),
    path('investor_dashboard/', views.investor_dashboard, name='investor_dashboard'),
    path('ideas/', views.manage_ideas, name='manage_ideas'),
    path('profile/', views.profile, name='profile'),
    path('ideas/edit/<int:idea_id>/', views.edit_ideas, name='edit_ideas'),
    path('ideas/delete/<int:idea_id>/', views.delete_ideas, name='delete_ideas'),
    path('analyze_idea/<int:idea_id>/', views.analyze_idea, name='analyze_idea'),
    path('viewreport/<int:idea_id>/', views.viewreport, name='viewreport'),
    path('request_intro/<int:idea_id>/', views.request_introduction, name='request_introduction'),
    path('handle_request/<int:connection_id>/<str:action>/', views.handle_connection_request, name='handle_connection'),
    path('request/',views.request, name='request'),
    path('my_connections/', views.my_connections, name='my_connections'),
]
