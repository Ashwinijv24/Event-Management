from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_event, name='add_event'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('events/', views.view_events, name='view_events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('events/<int:event_id>/registrations/', views.event_registrations, name='event_registrations'),
    path('payment/<int:registration_id>/', views.payment, name='payment'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('ticket/<int:registration_id>/', views.ticket_view, name='ticket_view'),
    path('reports/', views.reports, name='reports'),
    
    # Admin URLs
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/<int:user_id>/edit-role/', views.edit_user_role, name='edit_user_role'),
    path('admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin/activity/', views.activity_log, name='activity_log'),
    
    # User Profile
    path('profile/', views.user_profile, name='user_profile'),
]
