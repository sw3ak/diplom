from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, UserUpdateSerializer
from .permissions import IsAdminOrSelf


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSelf]
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_superuser:
            allowed_fields = {'username', 'password'}
            for key in request.data.keys():
                if key not in allowed_fields:
                    return Response(
                        {"detail": "Вы можете обновлять только username и password."},
                        status=status.HTTP_403_FORBIDDEN
                    )
        return super().update(request, *args, **kwargs)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(username=request.data['username'])
        user_data = UserSerializer(user).data
        response.data['user'] = user_data
        return response
