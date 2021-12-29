from django.contrib import admin
from django.urls import path

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from testapp import views

schema_view = get_schema_view(
    openapi.Info(
        title="Test app API",
        default_version='v1',
        description="Test description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/login/', views.LogingAPIView.as_view()),
    path('api/login/code/', views.LogingCodeAPIView.as_view()),
    path('api/logout/', views.LogoutAPIView.as_view()),
    path('api/recovery/', views.RecoveryAPIView.as_view()),
    path('api/profile/', views.UserProfileRetrieveUpdateAPIView.as_view()),
    path('api/profile/rate/', views.UserRateAPIView.as_view()),
    path('api/operations/', views.TransactionListAPIView.as_view()),
    path('api/operations/<int:id>/', views.TransactionRetrieveAPIView.as_view()),
    path('api/operations/<int:operation_id>/feedbacks/', views.FeedBackCreateOperationAPIView.as_view()),
    path('api/bankcards/', views.BankCardListCreateAPIView.as_view()),
    path('api/bankcards/<int:id>/', views.BankCardRetrieveUpdateAPIView.as_view()),
    path('api/bankcards/<int:bank_card_id>/feedbacks/', views.FeedBackCreateBankCardAPIView.as_view()),
    path('api/feedbacks/', views.FeedBackListCreateAPIView.as_view()),
    path('api/feedbacks/<int:id>/', views.FeedBackRetrieveAPIView.as_view()),
]

urlpatterns += [
    path('admin/', admin.site.urls),
]
