from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('facilities/', views.facility_list, name='facility_list'),
    path('facilities/add/', views.add_facility, name='add_facility'),
    path('facilities/edit/<int:facility_id>/',views.edit_facility,name='edit_facility'),
    path('facilities/delete/',views.delete_facility,name='delete_facility'),
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('accounts/edit/<int:user_id>/', views.edit_account, name='edit_account'),
    path('accounts/delete/',views.delete_account,name='delete_account'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('reservations/all/', views.reservation_list, name='reservation_list'),
    path('reservations/create/', views.create_reservation_page, name='create_reservation'),
    path('reservations/add/', views.add_reservation, name='add_reservation'),
    path('reservations/approve/', views.approve_request, name='approve_request'),
    path('reservations/reject/', views.reject_request, name='reject_request'),
    path('api/reservations/', views.reservation_events, name='reservation_events')
]