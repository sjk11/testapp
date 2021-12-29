from random import randint
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from rest_framework.authtoken.models import Token


class User(AbstractUser):
    birth_date = models.DateField(blank=True, default=None, null=True)
    patronymic = models.CharField(max_length=32, verbose_name='Отчество', blank=True, default='')
    pincode = models.CharField(max_length=4, blank=True, default='')
    fingerprint = models.CharField(max_length=512, blank=True, default='')

    @property
    def bank_card(self):
        return self.bankcard_set.filter(is_default=True).last()


class UserRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='extra')
    rate = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    msg = models.TextField(verbose_name='Текст сообщения', blank=True, default='')


class BankCard(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.PROTECT)
    card_number = models.CharField(max_length=16, verbose_name='Номер карты')
    month = models.PositiveSmallIntegerField(verbose_name='Месяц', validators=[
        MaxValueValidator(12),
        MinValueValidator(1)
    ])
    year = models.PositiveSmallIntegerField(verbose_name='Месяц')
    first_name = models.CharField(max_length=32, verbose_name='Имя')
    last_name = models.CharField(max_length=32, verbose_name='Фамилия')
    STATUS_NEW, STATUS_ACTIVE, STATUS_BLOCKED = 'NEW', 'ACTIVE', 'BLOCKED'
    STATUS_CHOICES = (
        (STATUS_NEW, 'Не активна'),
        (STATUS_ACTIVE, 'Активна'),
        (STATUS_BLOCKED, 'Заблокирована'),
    )
    status = models.CharField(max_length=32,
                              db_index=True,
                              verbose_name='Статус обращения',
                              choices=STATUS_CHOICES)
    is_default = models.BooleanField(default=False, verbose_name='Основная карта')

    class Meta:
        verbose_name = 'Банковская карта'
        verbose_name_plural = 'Банковские карты'

    def _set_is_default(self):
        if self.__class__.objects.filter(user=self.user, is_default=True).exists() is False:
            self.is_default = True
        elif self.is_default:
            qs = self.__class__.objects.filter(user=self.user, is_default=True)
            if self.pk is not None:
                qs.exclude(pk=self.pk).update(is_default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._set_is_default()


class Transaction(models.Model):
    STATUS_NEW, STATUS_PROCESS, STATUS_BLOCKED, STATUS_CLOSE, STATUS_CANCEL = 'NEW', 'PROCESS', 'BLOCKED', 'CLOSED', 'CANCEL'
    STATUS_CHOICES = (
        (STATUS_NEW, 'Новая'),
        (STATUS_PROCESS, 'В процессе'),
        (STATUS_BLOCKED, 'Заблокирована'),
        (STATUS_CLOSE, 'Закрыто'),
        (STATUS_CANCEL, 'Отменена'),
    )
    bank_card = models.ForeignKey(BankCard, on_delete=models.PROTECT)
    amount = models.DecimalField(decimal_places=4, max_digits=32)
    title = models.CharField(max_length=32, verbose_name='Краткое описание', default='', blank=True)
    status = models.CharField(max_length=32,
                              db_index=True,
                              verbose_name='Статус обращения',
                              choices=STATUS_CHOICES)
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'


class RecoveryData(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.PROTECT)
    code = models.CharField(max_length=4)
    created_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Код востановления'
        verbose_name_plural = 'Код востановления'

    def _set_code(self):
        self.code = ''.join([randint(0, 9), randint(0, 9), randint(0, 9), randint(0, 9)])


class FeedBack(models.Model):
    TYPE_QUEST, TYPE_PROBLEM, TYPE_OPERATION, RECOVERY = 'QUEST', 'PROBLEM', 'OPERATION', 'RECOVERY'
    STATUS_NEW, STATUS_PROCESS, STATUS_CLOSE = 'NEW', 'PROCESS', 'CLOSE'
    TYPE_CHOICES = (
        (TYPE_QUEST, 'Обращение'),
        (TYPE_PROBLEM, 'Проблема'),
        (RECOVERY, 'Востановление'),
        (TYPE_OPERATION, 'Спорная операция'),
    )
    STATUS_CHOICES = (
        (STATUS_NEW, 'Новое'),
        (STATUS_PROCESS, 'В процессе'),
        (STATUS_CLOSE, 'Закрыто'),
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.PROTECT)
    feedback_type = models.CharField(max_length=32,
                                     db_index=True,
                                     verbose_name='Тип обращения',
                                     choices=TYPE_CHOICES)
    status = models.CharField(max_length=32,
                              db_index=True,
                              verbose_name='Статус обращения',
                              choices=STATUS_CHOICES)
    msg = models.TextField(verbose_name='Текст сообщения', blank=True, default='')
    answer = models.TextField(verbose_name='Ответ на Обращение', blank=True, default='')
    bank_card = models.ForeignKey(BankCard, on_delete=models.CASCADE, null=True, default=None, related_name='feedbacks')
    operation = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, default=None, related_name='feedbacks')
    recovery = models.ForeignKey(RecoveryData, on_delete=models.CASCADE, null=True, default=None, related_name='feedbacks')
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
