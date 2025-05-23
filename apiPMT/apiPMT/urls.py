from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.users.views import UserViewSet, RegisterView, CustomTokenObtainPairView
from app.teams.views import TeamViewSet
from app.users.permissions import IsSuperuserOrTechDir
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'teams', TeamViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[IsSuperuserOrTechDir]), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[IsSuperuserOrTechDir]), name='swagger-ui'),
]