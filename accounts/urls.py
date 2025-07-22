from .import views
from django.urls import path

urlpatterns = [
    path ('login/', views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path ('investor_login/', views.investor_login,name='investor_login'),
    path('investor_signup/',views.investor_signup,name='investor_signup'),
    path ('logout/', views.logout,name='logout')
]
