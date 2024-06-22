# website/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('service/', views.service, name='service'),
    path('feature/', views.feature, name='feature'),
    path('quote/', views.quote, name='quote'),
    path('404/', views.error_404, name='404'),
    path('login/', views.login, name = 'admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_company/', views.add_company, name = 'add_company'),
    path('company/<int:company_id>/', views.company_detail, name='company_detail'),
    path('add_trip/', views.add_trip, name='add_trip'),
    path('download_invoice/<int:company_id>/', views.download_invoice, name='download_invoice'),
    path('trip/<int:trip_id>/delete/', views.delete_trip, name='delete_trip'),
    path('trip/<int:trip_id>/update/', views.update_trip, name='update_trip'),
]
