from django.db import models


class Lottery(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, blank=True, null=True)
    description = models.CharField(blank=True, null=True)
    create = models.DateTimeField(blank=True, null=True)

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
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    full_name = models.CharField(blank=True, null=True)
    full_name_from_tg = models.CharField(blank=True, null=True)
    username = models.CharField(blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'users'
