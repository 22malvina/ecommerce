#!-*-coding: utf-8 -*-
from django.db import models
#from django.db.models import Count, Min, Sum, Avg
from django.db.models import Sum


class PlanFactEvent(models.Model):
    """
    Движение оборотных средств. Product, Money, ...
    """
    datetime_create = models.DateTimeField(u'дата и время создание', auto_now_add=True)

    is_plan = models.BooleanField(verbose_name=u'План', default=False)
    is_fact = models.BooleanField(verbose_name=u'Факт', default=False)

    is_in = models.BooleanField(verbose_name=u'Пришло', default=False)
    is_out = models.BooleanField(verbose_name=u'Ушло', default=False)

    invoice_guid = models.CharField(u'GUID накладной', max_length=200, null=True, blank=True)
    datetime_process = models.DateTimeField(u'дата и время проведения опрерации', null=True, blank=True)

    #Product
    #product = models.ForeignKey(Product, on_delete=models.CASCADE) # Следует использовать Guid Product.
    product_guid = models.IntegerField(u"guid продукта сейчас соответствует id этого product у нас в системе, так себе решение")
    article = models.CharField(u'Артикул продукта', max_length=200, null=True, blank=True)
    serial_number = models.CharField(u"Серийны номер/как персона", max_length=200, null=True, blank=True)
    quantity = models.IntegerField(u"Количество - участвует вов сех движениях по товарам")
    #storage = models.ForeignKey(Storage, on_delete=models.CASCADE) # Следует использовать Guid Storage.
    storage_guid = models.IntegerField(u"guid склада сейчас соответствует id этого storage у нас в системе, так себе решение", null=True, blank=True)
    #transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    transport_guid = models.IntegerField(u"guid транспорта сейчас соответствует id этого transport у нас в системе, так себе решение", null=True, blank=True)

    currency = models.CharField(u"Валюта закупки / реализации", max_length=200, null=True, blank=True)
    price = models.DecimalField(u"Стоимость закупки одной штуки если товар входит в систему / реализцаии если выходит - появляется один раз когда позиция входит в систему, или проходит по всем изменениям?", decimal_places=2, max_digits=7, null=True, blank=True)

    #Money
    #bank_account = models.ForeignKey(BankAccount)
    #money_currency = models.CharField(u"Валюта", max_length=200, null=True, blank=True)
    #money_value = models.DecimalField(u"Размер средств в конкретной валюте", decimal_places=2, max_digits=7, null=True, blank=True)

    #Repository
    @staticmethod
    def count_product(storage_guids, product_guids):
        quantity = 0
        # меделенно можно через сумму
        #if product_guids and storage_guids:
        #    for plan_fact_event in PlanFactEvent.objects.filter(storage_guid__in=storage_guids, product_guid__in=product_guids, is_in=True, is_out=False, is_plan=False, is_fact=True):
        #        quantity += plan_fact_event.quantity
        #    for plan_fact_event in PlanFactEvent.objects.filter(storage_guid__in=storage_guids, product_guid__in=product_guids, is_in=False, is_out=True, is_plan=False, is_fact=True):
        #        quantity -= plan_fact_event.quantity
        #elif product_guids:
        #    for plan_fact_event in PlanFactEvent.objects.filter(product_guid__in=product_guids, is_in=True, is_out=False, is_plan=False, is_fact=True):
        #        quantity += plan_fact_event.quantity
        #    for plan_fact_event in PlanFactEvent.objects.filter(product_guid__in=product_guids, is_in=False, is_out=True, is_plan=False, is_fact=True):
        #        quantity -= plan_fact_event.quantity
        #elif storage_guids:
        #    for plan_fact_event in PlanFactEvent.objects.filter(storage_guid__in=storage_guids, is_in=True, is_out=False, is_plan=False, is_fact=True):
        #        quantity += plan_fact_event.quantity
        #    for plan_fact_event in PlanFactEvent.objects.filter(storage_guid__in=storage_guids, is_in=False, is_out=True, is_plan=False, is_fact=True):
        #        quantity -= plan_fact_event.quantity
        #else:
        #    for plan_fact_event in PlanFactEvent.objects.filter(is_in=True, is_out=False, is_plan=False, is_fact=True):
        #        quantity += plan_fact_event.quantity
        #    for plan_fact_event in PlanFactEvent.objects.filter(is_in=False, is_out=True, is_plan=False, is_fact=True):
        #        quantity -= plan_fact_event.quantity
        #    #assert False

        #quantity__sum = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, product_guid__in=product_guids, is_in=True, is_out=False, is_plan=False, is_fact=True).aggregate(Sum('quantity'))
        if product_guids and storage_guids:
            quantity__sum_in = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, product_guid__in=product_guids, is_in=True, is_out=False, is_plan=False, is_fact=True).aggregate(Sum('quantity'))
            quantity__sum_out = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, product_guid__in=product_guids, is_in=False, is_out=True, is_plan=False, is_fact=True).aggregate(Sum('quantity'))
        elif product_guids and not storage_guids:
            quantity__sum_in = PlanFactEvent.objects.filter(product_guid__in=product_guids, is_in=True, is_out=False, is_plan=False, is_fact=True).aggregate(Sum('quantity'))
            quantity__sum_out = PlanFactEvent.objects.filter(product_guid__in=product_guids, is_in=False, is_out=True, is_plan=False, is_fact=True).aggregate(Sum('quantity'))
        elif not product_guids and storage_guids:
            quantity__sum_in = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, is_in=True, is_out=False, is_plan=False, is_fact=True).aggregate(Sum('quantity'))
            quantity__sum_out = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, is_in=False, is_out=True, is_plan=False, is_fact=True).aggregate(Sum('quantity'))
        else:
            quantity__sum_in = PlanFactEvent.objects.filter(is_in=True, is_out=False, is_plan=False, is_fact=True).aggregate(Sum('quantity'))
            quantity__sum_out = PlanFactEvent.objects.filter(is_in=False, is_out=True, is_plan=False, is_fact=True).aggregate(Sum('quantity'))

        if quantity__sum_in and quantity__sum_in.get('quantity__sum', 0):
            quantity += quantity__sum_in.get('quantity__sum', 0)
        #quantity__sum = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, product_guid__in=product_guids, is_in=False, is_out=True, is_plan=False, is_fact=True).aggregate(Sum('quantity')).get('quantity__sum', 0)
        if quantity__sum_out and quantity__sum_out.get('quantity__sum', 0):
            quantity -= quantity__sum_out.get('quantity__sum', 0)

        if quantity < 0:
            assert False
        return quantity

    @staticmethod
    def push_stocks(storage_guid, product_guid, quantity, currency, price):
        plan_fact_event = PlanFactEvent.objects.create(
            storage_guid=storage_guid,
            product_guid=product_guid,
            quantity=quantity,
            currency=currency,
            price=price,
            is_in=True,
            is_out=False,
            is_plan=False,
            is_fact=True)

    @staticmethod
    def pull_stocks(storage_guid, product_guid, quantity, currency, price):
        plan_fact_event = PlanFactEvent.objects.create(
            storage_guid=storage_guid,
            product_guid=product_guid,
            quantity=quantity,
            currency=currency,
            price=price,
            is_in=False,
            is_out=True,
            is_plan=False,
            is_fact=True)

    @staticmethod
    def product_guids_by_storage_guids(storage_guids):
        """
        Метод работает не коректно, он показыват все продукты которые были и есть на складе.
        Нужно чтобы только те которые сейчас в наличии.
        """
        #storage_guids_product_guids_quantity = {}
        product_guids = set()
        if storage_guids:
            for plan_fact_event in PlanFactEvent.objects.filter(storage_guid__in=storage_guids, is_in=True, is_out=False, is_plan=False, is_fact=True):
                #storage_guids_product_guids_quantity[plan_fact_event.storage_guid].set(plan_fact_event.product_guid, 0)
                product_guids.add(plan_fact_event.product_guid)
            for plan_fact_event in PlanFactEvent.objects.filter(storage_guid__in=storage_guids, is_in=False, is_out=True, is_plan=False, is_fact=True):
                #product_guids.add(fact_event.product_guid)
                #product_guids.add(plan_fact_event.product_guid)
                pass
        else:
            for plan_fact_event in PlanFactEvent.objects.filter(is_in=True, is_out=False, is_plan=False, is_fact=True):
                #quantity += plan_fact_event.quantity
                product_guids.add(plan_fact_event.product_guid)
            for plan_fact_event in PlanFactEvent.objects.filter(is_in=False, is_out=True, is_plan=False, is_fact=True):
                #quantity -= plan_fact_event.quantity
                pass
        return list(product_guids)


