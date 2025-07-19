from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('upload/', views.upload_file, name='upload'),
    path('download/<int:file_id>/', views.download_file, name='download'),
    path('download-pdf/<int:file_id>/', views.download_pdf, name='download_pdf'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('download/<int:file_id>/', views.download_file, name='download'),

]
