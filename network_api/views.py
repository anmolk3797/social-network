from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, CreateAPIView
from .serializers import LoginSerializer, SignupSerializer, UserSerializer, FriendRequestSerializer
from .utils import AppResponse, AuthService
from .constants import UserSignupMessages
from rest_framework import generics
from .models import CustomUser, FriendRequest
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle

app_response = AppResponse()


class LoginAPIView(GenericAPIView):
    """
    API view for user login.
    """

    permission_classes = ()
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle user login and authentication.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A success response containing authentication tokens on successful login.
                    An error response on failure.

        Raises:
            ValidationError: If the serializer validation fails.
            Exception: If any other exception occurs during the login process.
        """
        try:
            serializer = self.serializer_class(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            return app_response.success(
                **AuthService().get_auth_tokens_for_user(serializer.validated_data),
            )
        except ValidationError as e:
            raise e
        except Exception as e:
            return app_response.error(messages=str(e))


class RegistrationAPIView(CreateAPIView):
    """
    API view for User registration
    """

    serializer_class = SignupSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        """
        Create a new User instance.
        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        Raises:
            ValidationError: If the serializer validation fails.
            Exception: If any other exception occurs during the creation process.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return app_response.success(messages=UserSignupMessages.SUCCESS_MESSAGE)
        except ValidationError as e:
            raise e
        except Exception as e:
            return app_response.error(messages=str(e))
        
        
class UserSearchAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    

class FriendRequestThrottle(UserRateThrottle):
    scope = 'friend_request'
    rate = '3/minute'

    
class SendFriendRequestAPIView(APIView):
    throttle_classes = [FriendRequestThrottle]
    
    def post(self, request, receiver_id):
        sender = request.user
        receiver = CustomUser.objects.get(id=receiver_id)
        if sender == receiver:
            return Response({"error": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)
        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)
        if FriendRequest.objects.filter(sender=receiver, receiver=sender).exists():
            return Response({"error": "Friend request already received."}, status=status.HTTP_400_BAD_REQUEST)
        friend_request = FriendRequest.objects.create(sender=sender, receiver=receiver)
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AcceptFriendRequestAPIView(APIView):
    def post(self, request, request_id):
        friend_request = FriendRequest.objects.get(id=request_id)
        if friend_request.receiver != request.user:
            return Response({"error": "You are not authorized to accept this friend request."}, status=status.HTTP_401_UNAUTHORIZED)
        friend_request.accept()
        return Response({"message": "Friend request accepted successfully."}, status=status.HTTP_200_OK)


class RejectFriendRequestAPIView(APIView):
    def post(self, request, request_id):
        friend_request = FriendRequest.objects.get(id=request_id)
        if friend_request.receiver != request.user:
            return Response({"error": "You are not authorized to reject this friend request."}, status=status.HTTP_401_UNAUTHORIZED)
        friend_request.reject()
        return Response({"message": "Friend request rejected successfully."}, status=status.HTTP_200_OK)


class ListFriendsAPIView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        friend_requests_sent = FriendRequest.objects.filter(sender=user, accepted=True).values_list('receiver_id', flat=True)
        friend_requests_received = FriendRequest.objects.filter(receiver=user, accepted=True).values_list('sender_id', flat=True)
        friend_ids = set(friend_requests_sent) | set(friend_requests_received)
        return CustomUser.objects.filter(id__in=friend_ids)
    

class ListPendingFriendRequestsAPIView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, accepted=False)

