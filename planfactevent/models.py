#!-*-coding: utf-8 -*-
from django.db import models
#from django.db.models import Count, Min, Sum, Avg
from django.db.models import Sum


class PlanFactEvent(models.Model):
    """
    Движение оборотных средств. Product, Money, ...

    Первый этап, разарботки системы:
        Всегда работаем с серийниками
        В каждой накладной укзааны серийники.
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
    #article = models.CharField(u'Артикул продукта', max_length=200, null=True, blank=True)
    serial_number = models.CharField(u"Серийны номер/как персона", max_length=200, null=True, blank=True)
    quantity = models.IntegerField(u"Количество - участвует вов сех движениях по товарам")
    #quantity_from
    #quantity_to
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

    #@classmethod
    #def list(cls, storage_guids, product_guids):
    #    if product_guids and storage_guids:
    #        plan_fact_events_in = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, product_guid__in=product_guids, is_in=True, is_out=False, is_plan=False, is_fact=True)
    #        plan_fact_events_out = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, product_guid__in=product_guids, is_in=False, is_out=True, is_plan=False, is_fact=True)
    #    elif product_guids and not storage_guids:
    #        plan_fact_events_in = PlanFactEvent.objects.filter(product_guid__in=product_guids, is_in=True, is_out=False, is_plan=False, is_fact=True)
    #        plan_fact_events_out = PlanFactEvent.objects.filter(product_guid__in=product_guids, is_in=False, is_out=True, is_plan=False, is_fact=True)
    #    elif not product_guids and storage_guids:
    #        plan_fact_events_in = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, is_in=True, is_out=False, is_plan=False, is_fact=True)
    #        plan_fact_events_out = PlanFactEvent.objects.filter(storage_guid__in=storage_guids, is_in=False, is_out=True, is_plan=False, is_fact=True)
    #    else:
    #        plan_fact_events_in = PlanFactEvent.objects.filter(is_in=True, is_out=False, is_plan=False, is_fact=True)
    #        plan_fact_events_out = PlanFactEvent.objects.filter(is_in=False, is_out=True, is_plan=False, is_fact=True)

    @classmethod
    def __create_stock_with_serial_number(cls, plan_fact_events):
        """
        создает словари по событиям перемещений продуктов.
        """
        if not plan_fact_events.quantity == 1:
            # серийные товары всегда в колличестве 1
            assert False
        #return {
        #    #'is_in': plan_fact_event.is_in,
        #    #'is_out': plan_fact_event.is_out,
        #    #'datetime_process': plan_fact_event.datetime_process,
        #    'product_guid': plan_fact_events.product_guid,
        #    'serial_number': plan_fact_events.serial_number,
        #    #'storage_guid': storage_guid,
        #    'quantity': plan_fact_events.quantity,
        #    'currency': plan_fact_events.currency,
        #    'price': plan_fact_events.price,
        #}
        return (
            plan_fact_events.product_guid,
            plan_fact_events.serial_number,
            plan_fact_events.quantity,
            plan_fact_events.currency,
            plan_fact_events.price,
        )

    @classmethod
    def __list_fact_for_storage_guid_product_guid_sort_by_datetime_process(cls, storage_guid, product_guid):
        #plan_fact_events_in = PlanFactEvent.objects.filter(storage_guid=storage_guid, product_guid=product_guid, is_in=True, is_out=False, is_plan=False, is_fact=True)
        #plan_fact_events_out = PlanFactEvent.objects.filter(storage_guid=storage_guid, product_guid=product_guid, is_in=False, is_out=True, is_plan=False, is_fact=True)
        #return plan_fact_events_in + plan_fact_events_out
        #return PlanFactEvent.objects.filter(storage_guid=storage_guid, product_guid=product_guid, is_plan=False, is_fact=True).sort_by('datetime_process')
        return PlanFactEvent.objects.filter(storage_guid=storage_guid, product_guid=product_guid, is_plan=False, is_fact=True).order_by('datetime_process')

    @classmethod
    def stocks_with_serial_number_readey_for_move(cls, storage_guid, product_guid):
        """
        Простое перемещенеи между складами организации, поэтому изменния цены ен происходит.
        В дальнейшем можно будет проводить оперцию по изменрию цены при порче позиции при транспортировке или ...

        Только для товаров с серийниками.
        """
        stocks_with_serial = set()
        for plan_fact_event in cls.__list_fact_for_storage_guid_product_guid_sort_by_datetime_process(storage_guid, product_guid):
            stock_with_serial_number = cls.__create_stock_with_serial_number(plan_fact_event)
            #if cls.__create_stock_with_serial_number(plan_fact_event) in stocks_with_serial:
            if stock_with_serial_number in stocks_with_serial:
                if plan_fact_event.is_in and not plan_fact_event.is_out:
                    assert False
                elif not plan_fact_event.is_in and plan_fact_event.is_out:
                    #stocks_with_serial.remove(cls.__create_stocks_with_serial_number(plan_fact_event))
                    stocks_with_serial.remove(stock_with_serial_number)
                else:
                    assert False
            else:
                if plan_fact_event.is_in and not plan_fact_event.is_out:
                    #stocks_with_serial.add(cls.__create_stocks_with_serial_number(plan_fact_event))
                    stocks_with_serial.add(stock_with_serial_number)
                elif not plan_fact_event.is_in and plan_fact_event.is_out:
                    assert False
                else:
                    assert False
        return list(stocks_with_serial)


    @classmethod
    def count_product_with_serial_number(cls, storage_guids, product_guids):
        stocks_with_serial_number = []
        for storage_guid in storage_guids:
            for product_guid in product_guids:
                for stock_with_serial_number in cls.stocks_with_serial_number_readey_for_move(storage_guid, product_guid):
                    stocks_with_serial_number.append(stock_with_serial_number)
        return len(stocks_with_serial_number)

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
    def push_stocks(datetime_process, storage_guid, product_guid, quantity, currency, price):
        plan_fact_event = PlanFactEvent.objects.create(
            datetime_process=datetime_process,
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
    def push_stocks_witn_serial_number(datetime_process, storage_guid, stocks_with_serial_number):
        #plan_fact_event = PlanFactEvent.objects.create(
        #    datetime_process = datetime_process,
        #    storage_guid = storage_guid,
        #    product_guid = stocks_with_serial_number['product_guid'],
        #    serial_number = stocks_with_serial_number['serial_number'],
        #    quantity = stocks_with_serial_number['quantity'],
        #    currency = stocks_with_serial_number['currency'],
        #    price = stocks_with_serial_number['price'],
        #    is_in = True,
        #    is_out = False,
        #    is_plan = False,
        #    is_fact = True)
        plan_fact_event = PlanFactEvent.objects.create(
            datetime_process = datetime_process,
            storage_guid = storage_guid,
            product_guid = stocks_with_serial_number[0],
            serial_number = stocks_with_serial_number[1],
            quantity = stocks_with_serial_number[2],
            currency = stocks_with_serial_number[3],
            price = stocks_with_serial_number[4],
            is_in = True,
            is_out = False,
            is_plan = False,
            is_fact = True)

    @staticmethod
    def pull_stocks(datetime_process, storage_guid, product_guid, quantity, currency, price):
        plan_fact_event = PlanFactEvent.objects.create(
            datetime_process=datetime_process,
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
    def pull_stocks_witn_serial_number(datetime_process, storage_guid, stocks_with_serial_number):
        #plan_fact_event = PlanFactEvent.objects.create(
        #    datetime_process = datetime_process,
        #    storage_guid = storage_guid,
        #    product_guid = stocks_with_serial_number['product_guid'],
        #    serial_number = stocks_with_serial_number['serial_number'],
        #    quantity = stocks_with_serial_number['quantity'],
        #    currency = stocks_with_serial_number['currency'],
        #    price = stocks_with_serial_number['price'],
        #    is_in = False,
        #    is_out = True,
        #    is_plan = False,
        #    is_fact = True)
        plan_fact_event = PlanFactEvent.objects.create(
            datetime_process = datetime_process,
            storage_guid = storage_guid,
            product_guid = stocks_with_serial_number[0],
            serial_number = stocks_with_serial_number[1],
            quantity = stocks_with_serial_number[2],
            currency = stocks_with_serial_number[3],
            price = stocks_with_serial_number[4],
            is_in = False,
            is_out = True,
            is_plan = False,
            is_fact = True)

    @staticmethod
    def pull_transfer(datetime_process, transport_guid, stocks_with_serial_number):
        pass

    @staticmethod
    def push_transfer(datetime_process, transport_guid, stocks_with_serial_number):
        pass

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

    #@classmethod
    #def transfer_plan(cls, product_guid, quantity, currency, price, storage_guid_depart, datetime_depart, storage_guid_arrival, datetime_arrival):
    #    cls.pull_stocks(datetime_depart, storage_guid_depart, product_guid, quantity, currency, price)
    #    cls.push_stocks(datetime_arrival, storage_guid_arrival, product_guid, quantity, currency, price)

    def __unicode__(self):
        return u"id: %s %s %s %s %s %s %s product_guid: %s %s %s storage_guid: %s %s %s %s" % (self.id, self.is_plan, self.is_fact, self.is_in, self.is_out, self.invoice_guid, self.datetime_process, self.product_guid, self.serial_number, self.quantity, self.storage_guid, self.transport_guid, self.currency, self.price)

class ServiceTransferProductFromTo(object):
    def move(self, product_guid, quantity_for_transfer, storage_depart_guid, datetime_depart, transport_guid, storage_arrival_guid, datetime_arrival):
        #Получить столько информаци по имеющимся сейчас релальным товарам на складе чтобы потом их же списать, транспортировать и принять уже на другом.
        # транзакция с локом на чтение конкртеных записей, нужна для того чтобы при вытаскиваннии из событий того что приняли и хотим сейчас перевести. 
        #  Не встрял другой конкурирующий процес и не увез товары под другое перемещение.
        #   Если такое произойдет то в двух накладных на списание может фигурировать товар с одим и темже серийником.

        #start transaction
        #получить сейрийники подходящих товаров
        stocks_with_serial_number_readey_for_move = PlanFactEvent.stocks_with_serial_number_readey_for_move(storage_depart_guid, product_guid)
        #выбрать столько сколько нужно.
        stocks_with_serial_number = stocks_with_serial_number_readey_for_move[:quantity_for_transfer]
        #залочить их для других перемещений
        #    если не получилось залочить получить другие без этих
        #списать их с склада
        for stock_with_serial_number in stocks_with_serial_number:
            PlanFactEvent.pull_stocks_witn_serial_number(datetime_depart, storage_depart_guid, stock_with_serial_number)
        #снять блокировку
        #принять их к перемещению
        for stock_with_serial_number in stocks_with_serial_number:
            PlanFactEvent.push_transfer(datetime_depart, transport_guid, stock_with_serial_number)
        #списать их с перемещения
        for stock_with_serial_number in stocks_with_serial_number:
            PlanFactEvent.pull_transfer(datetime_arrival, transport_guid, stock_with_serial_number)
        #приянть их на складе получателе
        for stock_with_serial_number in stocks_with_serial_number:
            PlanFactEvent.push_stocks_witn_serial_number(datetime_arrival, storage_arrival_guid, stock_with_serial_number)
        #finish transaction


