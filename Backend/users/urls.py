from django.urls import path
from .views import LoginView, RegisterView  # Ensure these are imported

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # Use as_view()
    path('register/', RegisterView.as_view(), name='register'),  # Use as_view()
]
