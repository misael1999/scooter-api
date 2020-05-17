"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# JWT
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from scooter.users.views import CustomerTokenObtainPairView
# Views
from scooter.users.views import users as user_view
from scooter.users.views import customers as customer_view

router = DefaultRouter()
router.register(r'api/v1/users', user_view.UserViewSet, basename='user')
router.register(r'api/v1/customers', customer_view.CustomerViewSet, basename='customers')

urlpatterns = [
    # JWT
    path('api/v1/users/login/customer/', CustomerTokenObtainPairView.as_view(), name='token_obtain_pair_customer'),
    path('api/v1/users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/users/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Views
    path('', include(router.urls))
]
