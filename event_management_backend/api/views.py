from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, permissions, status, viewsets, mixins
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Event, RSVP
from .serializers import (
    EventSerializer,
    RSVPSerializer,
    SignupSerializer,
    UserSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@api_view(['GET'])
def health(request):
    """Health check endpoint."""
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
class SignupView(generics.CreateAPIView):
    """
    User signup endpoint (register new user).
    """
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Signup new user",
        operation_description="Register a new user with a username, password, and optional email.",
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# PUBLIC_INTERFACE
class LoginView(APIView):
    """
    User login endpoint - returns auth token.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Login user",
        operation_description="Authenticate existing user and return an auth token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format="password"),
            }
        ),
        responses={200: "Returns user info and token on success or error message on failure"}
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "user": UserSerializer(user).data
                }
            )
        return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
class EventViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Events.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        operation_summary="List events",
        operation_description="Get list of all events or filterable."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create event",
        operation_description="Create a new event with date, time, and location details."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update event",
        operation_description="Update details of an existing event."
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete event",
        operation_description="Delete an existing event."
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# PUBLIC_INTERFACE
class RSVPViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    """
    RSVP for events (respond/modify RSVP).
    """
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Respond to an Event (RSVP)",
        operation_description="RSVP to an event (yes, no, maybe). Requires auth.",
        responses={201: RSVPSerializer}
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Update RSVP",
        operation_description="Change your RSVP to an event."
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"error": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="My RSVPs",
        operation_description="List my RSVPs for events.",
        responses={200: RSVPSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """
        Returns a list of RSVPs for the current authenticated user.
        """
        my_rsvps = RSVP.objects.filter(user=request.user).select_related('event')
        serializer = RSVPSerializer(my_rsvps, many=True)
        return Response(serializer.data)
