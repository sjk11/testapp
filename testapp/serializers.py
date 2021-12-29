from rest_framework import serializers

from .models import BankCard, Transaction, FeedBack, User, RecoveryData


class BankCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankCard
        fields = ['id', 'card_number', 'month', 'year', 'first_name', 'last_name', 'status', 'is_default']
        read_only_fields = ('id', 'status')

    def create(self, validate_data):
        validate_data['author'] = self.context['user']
        return BankCard.objects.create(
            **validate_data
        )


class BankCardDetailSerializer(serializers.ModelSerializer):
    total_amount_limit = serializers.DecimalField(label='Общий доступный лимит', max_digits=15, decimal_places=2, default=0, read_only=True)
    cash_amount_limit = serializers.DecimalField(label='доступный лимит снятия наличных ', max_digits=15,
                                                 decimal_places=2, default=0, read_only=True)
    buy_amount_limit = serializers.DecimalField(label='доступный лимит покупок ', max_digits=15, decimal_places=2, default=0, read_only=True)

    class Meta:
        model = BankCard
        fields = ['id', 'card_number', 'month', 'year', 'first_name', 'last_name', 'status', 'is_default',
                  'total_amount_limit', 'cash_amount_limit', 'buy_amount_limit']
        read_only_fields = ('id', 'card_number', 'month', 'year', 'first_name', 'last_name', 'status',
                            'total_amount_limit', 'cash_amount_limit', 'buy_amount_limit')

    def create(self, validate_data):
        validate_data['author'] = self.context['user']
        return BankCard.objects.create(
            **validate_data
        )


class TransactionSerializer(serializers.ModelSerializer):
    bank_card = BankCardSerializer()

    class Meta:
        model = Transaction
        fields = ['id', 'bank_card', 'amount', 'status', 'created_dt', 'updated_dt']


class RecoveryDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecoveryData
        fields = ['id', 'code', 'created_dt', ]


class FeedBackListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeedBack
        fields = ['id', 'feedback_type', 'status',
                  'created_dt', 'updated_dt']
        read_only_fields = ['created_dt', 'updated_dt',
                            'id', 'status']

    def create(self, validate_data):
        validate_data['author'] = self.context['user']
        validate_data['feedback_type'] = self.context['feedback_type']
        validate_data['bank_card'] = self.context.get('bank_card')
        validate_data['operation'] = self.context.get('operation')
        validate_data['status'] = FeedBack.STATUS_NEW
        return FeedBack.objects.create(
            **validate_data
        )


class FeedBackBankCardCreateSerializer(FeedBackListSerializer):
    bank_card = BankCardSerializer(read_only=True)

    class Meta:
        model = FeedBack
        fields = ['id', 'feedback_type', 'status',
                  'created_dt', 'updated_dt', 'bank_card']
        read_only_fields = ['feedback_type', 'created_dt', 'updated_dt',
                            'id', 'status']


class FeedBackOperationSerializer(FeedBackListSerializer):
    operation = TransactionSerializer(read_only=True)

    class Meta:
        model = FeedBack
        fields = ['id', 'feedback_type', 'status',
                  'created_dt', 'updated_dt', 'operation']
        read_only_fields = ['feedback_type', 'created_dt', 'updated_dt',
                            'id', 'status']


class FeedBackDetailSerializer(serializers.ModelSerializer):
    bank_card = BankCardSerializer(read_only=True)
    operation = TransactionSerializer(read_only=True)

    class Meta:
        model = FeedBack
        fields = ['id', 'feedback_type', 'status',
                  'created_dt', 'updated_dt', 'bank_card', 'operation']
        read_only_fields = ['created_dt', 'updated_dt',
                            'id', 'status']


class UserProfileSerializer(serializers.ModelSerializer):
    is_pincode = serializers.SerializerMethodField()
    is_fingerprint = serializers.SerializerMethodField()
    bank_card = BankCardSerializer(read_only=True)
    total_amount_limit = serializers.DecimalField(label='Общий доступный лимит', max_digits=15, decimal_places=2, default=0)
    cash_amount_limit = serializers.DecimalField(label='доступный лимит снятия наличных ', max_digits=15, decimal_places=2, default=0)
    buy_amount_limit = serializers.DecimalField(label='доступный лимит покупок ', max_digits=15, decimal_places=2, default=0)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'patronymic', 'birth_date',
                  'is_pincode', 'is_fingerprint',
                  'bank_card',
                  'total_amount_limit', 'cash_amount_limit', 'buy_amount_limit']

    def get_is_pincode(self, user):
        return bool(user.pincode)

    def get_is_fingerprint(self, user):
        return bool(user.fingerprint)


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic', 'birth_date', 'pincode', 'fingerprint']
