from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import logout, authenticate

from rest_framework import status, authentication, exceptions, generics, permissions

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, BankCard, Transaction, UserRate, FeedBack
from .serializers import (BankCardSerializer, UserProfileSerializer, UserUpdateSerializer,
                          TransactionSerializer, BankCardDetailSerializer, FeedBackListSerializer,
                          FeedBackDetailSerializer, FeedBackBankCardCreateSerializer, FeedBackOperationSerializer)


class CustomAuthentication(authentication.BaseAuthentication):

    def authenticate(self, token=None, ):
        if token:
            # Change this to check time validity of token
            last_month = datetime.today() - timedelta(days=settings.TOKEN_EXPIRY_DAYS)
            try:
                user = User.objects.filter(
                    access_token=token,  # This should be unique
                    access_token_created_on__gte=last_month,
                )[0]
            except IndexError:
                return None
        elif username and password:
            # Assumes that email is unique
            try:
                user = User.objects.get(email=email)

                # Utilizes User.check_password()
                if not user.check_password(password):
                    return None
            except User.DoesNotExist:
                return None
        else:
            return None

        return user

    def _authenticate(self, request):
        username = request.META.get('HTTP_X_USERNAME')
        if not username:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)


class LogingAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        username, password = request.data.get('username'), request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            raise exceptions.AuthenticationFailed('No such user')
        return Response(status=status.HTTP_200_OK)


class LogingCodeAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        username, password = request.data.get('username'), request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            raise exceptions.AuthenticationFailed('No such user')
        return Response(status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    def post(self, request, format=None):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class RecoveryAPIView(APIView):
    def _get_user(self, data):
        username = data.get('username')
        if username:
            return User.objects.filter(username=username).first()
        first_name, last_name, patronymic, birth_date = data.get('first_name'), data.get('last_name'), data.get('patronymic'), data.get('birth_date')
        if all([first_name, last_name, patronymic, birth_date]):
            return User.objects.filter(
                first_name=first_name,
                last_name=last_name,
                patronymic=patronymic,
                birth_date=birth_date
            ).first()
        return None

    def get(self, request, format=None):
        user = self._get_user(request.query_params)
        if user is not None:
            raise exceptions.APIException('user not exists')
        return Response(status=status.HTTP_200_OK)

    def post(self, request, format=None):
        user = self._get_user(request.data)
        if user is not None:
            raise exceptions.APIException('user not exists')
        return Response(status=status.HTTP_200_OK)


class UserRateAPIView(APIView):
    def _get_user_rate(self, request):
        return UserRate.objects.filter(user=request.user).last()

    def get(self, request, format=None):
        user_rate = self._get_user(request)
        rate_data = {
            'rate': 0,
            'msg': '',
        }
        if user_rate is not None:
            rate_data['rate'] = user_rate.rate
            rate_data['msg'] = user_rate.msg
        return Response(rate_data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        user_rate = self._get_user(request)
        rate_data = {
            'rate': 0,
            'msg': '',
        }
        rate = int(request.data['rate']) if str(request.data.get('rate')).isdigit() else 0
        msg = request.data.get('msg') or ''
        if 1 <= rate <= 5:
            if user_rate is None:
                user_rate = UserRate.objects.create(
                    user=request.user, rate=rate, msg=msg)
            else:
                user_rate.rate = rate
                user_rate.msg = msg
                user_rate.save()
            rate_data['rate'] = user_rate.rate
            rate_data['msg'] = user_rate.msg
            return Response(rate_data, status=status.HTTP_200_OK)
        raise exceptions.APIException('rate min 1 max 5')


class BankCardListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BankCardSerializer

    def get_queryset(self):
        filters = dict(author=self.request.user)
        is_default = self.request.query_params.get('is_default')
        if is_default is not None:
            filters['is_default'] = str(is_default).lower() == 'true'
        return BankCard.objects.filter(
            **filters
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class FeedBackListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FeedBackListSerializer

    def get_queryset(self):
        filters = dict(author=self.request.user)
        return FeedBack.objects.filter(
            **filters
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['feedback_type'] = FeedBack.TYPE_QUEST
        return context


class FeedBackRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = FeedBackDetailSerializer

    def get_queryset(self):
        filters = dict(author=self.request.user)
        return FeedBack.objects.filter(
            **filters
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class FeedBackCreateBankCardAPIView(generics.CreateAPIView):
    serializer_class = FeedBackBankCardCreateSerializer

    def get_queryset(self):
        filters = dict(author=self.request.user)
        return FeedBack.objects.filter(
            **filters
        )

    def get_bank_card(self):
        filters = dict(
            author=self.request.user,
            id=self.kwargs.get('bank_card_id'),
        )
        return BankCard.objects.filter(
            **filters
        ).last()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['feedback_type'] = FeedBack.TYPE_PROBLEM
        context['bank_card'] = self.get_bank_card()
        return context


class FeedBackCreateOperationAPIView(generics.CreateAPIView):
    serializer_class = FeedBackOperationSerializer

    def get_queryset(self):
        filters = dict(author=self.request.user)
        return FeedBack.objects.filter(
            **filters
        )

    def get_operation(self):
        filters = dict(
            bank_card__author=self.request.user,
            id=self.kwargs.get('operation_id'),
        )
        return Transaction.objects.filter(
            **filters
        ).last()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['feedback_type'] = FeedBack.TYPE_OPERATION
        context['operation'] = self.get_operation()
        return context


class BankCardRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = BankCardDetailSerializer

    def get_queryset(self):
        filters = dict(author=self.request.user)
        return BankCard.objects.filter(
            **filters
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserUpdateSerializer
        return self.serializer_class


class TransactionListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        filters = dict(bank_card__author=self.request.user)
        is_default = self.request.query_params.get('is_default')
        bank_card = self.request.query_params.get('bank_card')
        if is_default is not None:
            filters['bank_card__is_default'] = str(is_default).lower() == 'true'
        if str(bank_card).isdigit():
            filters['bank_card_id'] = bank_card
        return Transaction.objects.filter(
            **filters
        )


class TransactionRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        filters = dict(bank_card__author=self.request.user)
        is_default = self.request.query_params.get('is_default')
        bank_card = self.request.query_params.get('bank_card')
        if is_default is not None:
            filters['bank_card__is_default'] = str(is_default).lower() == 'true'
        if str(bank_card).isdigit():
            filters['bank_card_id'] = bank_card
        return Transaction.objects.filter(
            **filters
        )
