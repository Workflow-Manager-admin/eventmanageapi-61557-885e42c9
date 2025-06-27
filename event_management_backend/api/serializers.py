from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Event, RSVP


# PUBLIC_INTERFACE
class SignupSerializer(serializers.ModelSerializer):
    """
    Signup request/response for new user registration.
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """
    User object output.
    """
    class Meta:
        model = User
        fields = ["id", "username", "email"]


# PUBLIC_INTERFACE
class EventSerializer(serializers.ModelSerializer):
    """
    Event serializer for CRUD endpoints.
    """
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


# PUBLIC_INTERFACE
class RSVPSerializer(serializers.ModelSerializer):
    """
    RSVP serializer for managing attendance.
    """
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        source='event',
        queryset=Event.objects.all(),
        write_only=True,
        required=True
    )

    class Meta:
        model = RSVP
        fields = ("id", "user", "event", "event_id", "response", "responded_at")
