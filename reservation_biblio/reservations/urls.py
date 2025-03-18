from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('validate_login/', views.validate_login, name='validate_login'),
    path('reservation/', views.reservation, name='reservation'),
    path('check_availability/<str:date_selected>/<str:room_name>/', views.check_availability, name='check_availability'),
    path('create_reservation/<date_selected>/<room_name>/<hour>/', views.create_reservation, name='create_reservation'),
    path('manage_reservations/', views.manage_reservations, name='manage_reservations'),
    path('cancel_reservation/<reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('logout/', views.logout, name='logout'),  
]
