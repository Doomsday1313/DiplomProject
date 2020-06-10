from django.db import models
from django.contrib.auth.models import User
import django.contrib.auth


class History(models.Model):
    name = models.CharField(max_length=100)
    datafile = models.FilePathField()
    inn = models.CharField(max_length=10)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


class Criteria(models.Model):
    avtonom = models.IntegerField()
    sosobesp = models.IntegerField()
    pokrinvest = models.IntegerField()
    CurrentRatio = models.IntegerField()
    QuickRatio = models.IntegerField()
    CashRatio = models.IntegerField()
    ROA = models.IntegerField()
    ProfitMargin = models.IntegerField()
    GrossMargin = models.IntegerField()
    mobilos = models.IntegerField()
    obesmpz = models.IntegerField()
    ICR = models.IntegerField()
    ROE = models.IntegerField()
    fondootd = models.IntegerField()
    AssetTurnover = models.IntegerField()
    ReceivablesTurnover = models.IntegerField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
