from django.contrib.auth import get_user_model
from rest_framework import generics, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSignupSerializer, UserLoginSerializer ,UserSerializer, UserNameUpdateSerializer,FriendRequestSerializer, FriendSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from .models import FriendRequest, CustomUser
from django.utils import timezone
from django.db.models import Q

User = get_user_model()


class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSignupSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            if 'unique constraint ' in str(e).lower():
                raise ValidationError('Email already exists')
            else:
                raise ValidationError("Unable to cretae User")
        
class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        user = authenticate(request,email=email,password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
            },status=status.HTTP_200_OK)
            
        else:
            return Response({
                'error': 'Invalid credentials'
            },status=status.HTTP_401_UNAUTHORIZED)
            
class UserSearchAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_keyword = self.request.query_params.get('search', None)
        if search_keyword:
            if User.objects.filter(email__iexact=search_keyword).exists():
                return queryset.filter(email__iexact=search_keyword)
            else:
                return queryset.filter(first_name__istartswith=search_keyword) | queryset.filter(last_name__istartswith=search_keyword)
        return queryset
    
    
class UserNameUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserNameUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    
class FriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        from_user = self.request.user
        to_user_id = self.request.data.get('to_user')
        try:
            to_user = CustomUser.objects.get(id=to_user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError('User does not exist.')
        
        if from_user == to_user:
            raise ValidationError('You cannot send a friend request to yourself.')
        
        if FriendRequest.objects.filter(from_user=from_user,to_user=to_user).exists():
            raise ValidationError('You have already sent a friend request to this user')
        
        # Limit to 3 requests per minute
        one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
        recents_requests = FriendRequest.objects.filter(from_user=from_user,timestamp__gte=one_minute_ago).count()
        if recents_requests > 3:
            raise ValidationError('You can only send 3 friend requests per minute')
        
        serializer.save(from_user=from_user,to_user=to_user)
        
class AcceptFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()
        friend_request.accepted = True
        friend_request.save()
        return Response({'status': 'friend request accepted'}, status=status.HTTP_200_OK)

    def get_object(self):
        try:
            return FriendRequest.objects.get(id=self.kwargs['pk'], to_user=self.request.user, accepted=False)
        except FriendRequest.DoesNotExist:
            raise ValidationError('No FriendRequest matches the given query.')

class RejectFriendRequestView(generics.DestroyAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return FriendRequest.objects.get(id=self.kwargs['pk'], to_user=self.request.user, accepted=False)
        except FriendRequest.DoesNotExist:
            raise ValidationError('No FriendRequest matches the given query.')

class ListFriendsView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        accepted_requests = FriendRequest.objects.filter(Q(from_user=user) | Q(to_user=user), accepted=True)
        friend_ids = [req.to_user.id if req.from_user == user else req.from_user.id for req in accepted_requests]
        return CustomUser.objects.filter(id__in=friend_ids)

class ListPendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, accepted=False)
    