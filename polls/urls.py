from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('polls/', views.poll_list, name='poll_list'),
    path('poll/<int:id>/', views.poll_detail, name='poll_detail'),
    path('poll/<int:id>/vote/', views.vote, name='vote'),
    path('poll/<int:id>/results/', views.poll_results, name='poll_results'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Poll management
    path('poll/create/', views.create_poll, name='create_poll'),
    path('poll/<int:id>/deactivate/', views.deactivate_poll, name='deactivate_poll'),
    path('poll/<int:id>/delete/', views.delete_poll, name='delete_poll'),
    path('my-polls/', views.my_polls, name='my_polls'),

    # Vote history
    path('history/', views.vote_history, name='vote_history'),

    # User profile
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
