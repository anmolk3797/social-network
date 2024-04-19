from rest_framework import serializers
from .models import CustomUser, FriendRequest
from .utils import normalize_email
from django.contrib.auth import authenticate
from .constants import AuthConstantsMessages, UserSignupMessages
from django.contrib.auth.password_validation import validate_password


class LoginSerializer(serializers.Serializer):
    """
    Serializer for Login
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        """
        Validate method for login serializer
        :param attrs: OrderedDict
        :return: user (User model instance)
        Raises:
            serializers.ValidationError: If the user entered wrong email id and password.
        """
        login_data = {
            "password": attrs.get("password"),
            "username": normalize_email(attrs.get("email")),
        }
        user = authenticate(**login_data)
        if not user:
            raise serializers.ValidationError(
                AuthConstantsMessages.INVALID_EMAIL_OR_PASSWORD
            )
        return user


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True, )

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "password", "confirm_password"]
        extra_kwargs = {
            "username": {"required": False},
        }

    def validate_password(self, password: str) -> str:
        """
        Validation method for the 'password' field.
        Args:
            password (str): The password value to be validated.
        Returns:
            str: The validated password value.
        Raises:
            serializers.ValidationError: If the password does not match the 'confirm_password' field.
        """
        confirm_password = self.initial_data.get("confirm_password")
        if password != confirm_password:
            raise serializers.ValidationError(
                UserSignupMessages.PASSWORD_NOT_MATCH_ERROR
            )
        return password

    def validate_email(self, email: str) -> str:
        """
        Validation method for the 'email' field.
        Args:
            email (str): The email value to be validated.
        Returns:
            str: The validated email value.
        Raises:
            serializers.ValidationError: If the email already exists in the User model.
        """
        email = normalize_email(email)
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(UserSignupMessages.EMAIL_EXIST_ERROR)
        return email


    def create(self, validated_data: dict) -> CustomUser:
        """This method creates a new instance of the User model based on the validated data.
        Args:
            validated_data (dict): The validated data for creating the User.
        Returns:
            user: The created User instance.
        """
        password = validated_data.pop("password")
        validated_data.pop("confirm_password")
        email = normalize_email(validated_data.get("email"))
        validated_data.update({"username": email})
        user = super().create(validated_data)
        user.set_password(password)
        user.save(update_fields=["password"])
        return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

    def to_representation(self, instance):
        """Custom representation to exclude sensitive fields."""
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'created_at', 'accepted']
