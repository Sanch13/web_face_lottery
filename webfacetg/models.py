from django.db import models
from django.urls import reverse


class Lottery(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    create = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("webfacetg:lottery_users", args=[self.id])

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'lotteries'


class Ticket(models.Model):
    id = models.BigAutoField(primary_key=True)
    ticket_number = models.IntegerField()
    create = models.DateTimeField(blank=True, null=True)
    lottery = models.ForeignKey(
        Lottery,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='tickets'
    )
    user = models.ForeignKey(
        'TelegramUser',
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='tickets'
    )

    class Meta:
        managed = False
        db_table = 'tickets'
        unique_together = (('user', 'lottery'),)


class TelegramUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    telegram_id = models.BigIntegerField(unique=True,
                                         blank=True,
                                         null=True)
    full_name = models.CharField(max_length=255,
                                 verbose_name='ФИО',
                                 blank=True,
                                 null=True)
    full_name_from_tg = models.CharField(max_length=255,
                                         verbose_name='ФИО из Телеграма',
                                         blank=True,
                                         null=True)
    username = models.CharField(max_length=255,
                                blank=True,
                                null=True)
    is_active = models.BooleanField()
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ID({self.id})"

    def get_absolute_url(self):
        return reverse("webfacetg:edit_users", args=[str(self.id)])

    def save(self, *args, **kwargs):
        kwargs['using'] = kwargs.get('using', 'psql')  # Указываем базу по умолчанию
        super().save(*args, **kwargs)

