from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health,
    SignupView,
    LoginView,
    EventViewSet,
    RSVPViewSet
)

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'rsvps', RSVPViewSet, basename='rsvp')

urlpatterns = [
    path('health/', health, name='Health'),

    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),

    path('', include(router.urls)),
]
