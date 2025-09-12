from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('simulations/', views.simulations_list, name='simulations_list'),
    path('simulations/<str:sim_id>/run/', views.run_simulation, name='run_simulation'),
    path('simulations/<str:sim_id>/pause/', views.pause_simulation, name='pause_simulation'),
    path('simulations/<str:sim_id>/state/', views.simulation_state, name='simulation_state'),
    path('replays/<str:replay_id>/', views.get_replay, name='get_replay'),
]