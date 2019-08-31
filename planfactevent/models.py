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

    @classmethod
    def count_product_with_serial_number(cls, storage_guids, product_guids):
        stocks_with_serial_number = []
        for storage_guid in storage_guids:
            for product_guid in product_guids:
                for stock_with_serial_number in cls.stocks_with_serial_number_ready_for_move(storage_guid, product_guid):
                    stocks_with_serial_number.append(stock_with_serial_number)
        return len(stocks_with_serial_number)

    def is_pull(self):
        if not self.is_in and self.is_out:
            return True
        return False

    def is_push(self):
        if self.is_in and not self.is_out:
            return True
        return False

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
    def list_for_fact_storage_guid_product_guid_sort_by_datetime_process(cls, storage_guid, product_guid):
        #plan_fact_events_in = PlanFactEvent.objects.filter(storage_guid=storage_guid, product_guid=product_guid, is_in=True, is_out=False, is_plan=False, is_fact=True)
        #plan_fact_events_out = PlanFactEvent.objects.filter(storage_guid=storage_guid, product_guid=product_guid, is_in=False, is_out=True, is_plan=False, is_fact=True)
        #return plan_fact_events_in + plan_fact_events_out
        #return PlanFactEvent.objects.filter(storage_guid=storage_guid, product_guid=product_guid, is_plan=False, is_fact=True).sort_by('datetime_process')
        return PlanFactEvent.objects.filter(storage_guid=storage_guid, product_guid=product_guid, is_plan=False, is_fact=True).order_by('datetime_process','product_guid','serial_number','currency','-price','quantity')

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

    #@staticmethod
    #def pull_stocks_witn_serial_number(datetime_process, storage_guid, stocks_with_serial_number):
    #    #plan_fact_event = PlanFactEvent.objects.create(
    #    #    datetime_process = datetime_process,
    #    #    storage_guid = storage_guid,
    #    #    product_guid = stocks_with_serial_number['product_guid'],
    #    #    serial_number = stocks_with_serial_number['serial_number'],
    #    #    quantity = stocks_with_serial_number['quantity'],
    #    #    currency = stocks_with_serial_number['currency'],
    #    #    price = stocks_with_serial_number['price'],
    #    #    is_in = False,
    #    #    is_out = True,
    #    #    is_plan = False,
    #    #    is_fact = True)
    #    plan_fact_event = PlanFactEvent.objects.create(
    #        datetime_process = datetime_process,
    #        storage_guid = storage_guid,
    #        product_guid = stocks_with_serial_number[0],
    #        serial_number = stocks_with_serial_number[1],
    #        quantity = stocks_with_serial_number[2],
    #        currency = stocks_with_serial_number[3],
    #        price = stocks_with_serial_number[4],
    #        is_in = False,
    #        is_out = True,
    #        is_plan = False,
    #        is_fact = True)

    @staticmethod
    def pull_transfer(datetime_process, transport_guid, stocks_with_serial_number):
        print 'Nead same code'
        pass

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

    #@staticmethod
    #def push_stocks_witn_serial_number(datetime_process, storage_guid, stocks_with_serial_number):
    #    #plan_fact_event = PlanFactEvent.objects.create(
    #    #    datetime_process = datetime_process,
    #    #    storage_guid = storage_guid,
    #    #    product_guid = stocks_with_serial_number['product_guid'],
    #    #    serial_number = stocks_with_serial_number['serial_number'],
    #    #    quantity = stocks_with_serial_number['quantity'],
    #    #    currency = stocks_with_serial_number['currency'],
    #    #    price = stocks_with_serial_number['price'],
    #    #    is_in = True,
    #    #    is_out = False,
    #    #    is_plan = False,
    #    #    is_fact = True)
    #    plan_fact_event = PlanFactEvent.objects.create(
    #        datetime_process = datetime_process,
    #        storage_guid = storage_guid,
    #        product_guid = stocks_with_serial_number[0],
    #        serial_number = stocks_with_serial_number[1],
    #        quantity = stocks_with_serial_number[2],
    #        currency = stocks_with_serial_number[3],
    #        price = stocks_with_serial_number[4],
    #        is_in = True,
    #        is_out = False,
    #        is_plan = False,
    #        is_fact = True)

    @staticmethod
    def push_transfer(datetime_process, transport_guid, stocks_with_serial_number):
        print 'Nead same code'
        pass

    @classmethod
    def stocks_with_serial_number_ready_for_move(cls, storage_guid, product_guid):
        """
        Простое перемещенеи между складами организации, поэтому изменния цены ен происходит.
        В дальнейшем можно будет проводить оперцию по изменрию цены при порче позиции при транспортировке или ...

        Только для товаров с серийниками.
        """
        #stocks_with_serial_number = set()
        stocks_with_serial_number = []
        for plan_fact_event in cls.list_for_fact_storage_guid_product_guid_sort_by_datetime_process(storage_guid, product_guid):
            #stock_with_serial_number = cls.__create_stock_with_serial_number(plan_fact_event)
            stock_with_serial_number = FactoryStockFromPlanFactEvent().create(plan_fact_event)
            #if cls.__create_stock_with_serial_number(plan_fact_event) in stocks_with_serial_number:
            if stock_with_serial_number in stocks_with_serial_number:
                if plan_fact_event.is_in and not plan_fact_event.is_out:
                    assert False
                elif not plan_fact_event.is_in and plan_fact_event.is_out:
                    #stocks_with_serial_number.remove(cls.__create_stocks_with_serial_number(plan_fact_event))
                    #stocks_with_serial_number.remove(stock_with_serial_number)
                    stocks_with_serial_number.remove(stock_with_serial_number)
                else:
                    assert False
            else:
                if plan_fact_event.is_in and not plan_fact_event.is_out:
                    #stocks_with_serial_number.add(cls.__create_stocks_with_serial_number(plan_fact_event))
                    #stocks_with_serial_number.add(stock_with_serial_number)
                    stocks_with_serial_number.append(stock_with_serial_number)
                elif not plan_fact_event.is_in and plan_fact_event.is_out:
                    # предполагается что всега в системе только положительные остатки
                    assert False
                else:
                    assert False
        return list(stocks_with_serial_number)

    @classmethod
    def storage_guids(cls):
        storage_guids = set()
        if plan_fact_event in PlanFactEvent.objects.all():
            storage_guids.add(plan_fact_event.storage_guid)
        return list(storage_guids)

    #@classmethod
    #def transfer_plan(cls, product_guid, quantity, currency, price, storage_guid_depart, datetime_depart, storage_guid_arrival, datetime_arrival):
    #    cls.pull_stocks(datetime_depart, storage_guid_depart, product_guid, quantity, currency, price)
    #    cls.push_stocks(datetime_arrival, storage_guid_arrival, product_guid, quantity, currency, price)

    def __unicode__(self):
        #return u"id: %s %s %s %s %s %s %s product_guid: %s %s %s storage_guid: %s %s %s %s" % (self.id, self.is_plan, self.is_fact, self.is_in, self.is_out, self.invoice_guid, self.datetime_process, self.product_guid, self.serial_number, self.quantity, self.storage_guid, self.transport_guid, self.currency, self.price)
        return u"id: %s %s %s %s %s product_guid: %s S\\N: %s quantity: %s storage_guid: %s transport_guid: %s %s %s" % (
            self.id,
            'Plan' if self.is_plan and not self.is_fact else 'Fact' if not self.is_plan and self.is_fact else 'Error',
            'In' if self.is_in and not self.is_out else 'Out' if not self.is_in and self.is_out else 'Error',
            self.invoice_guid, self.datetime_process, self.product_guid, self.serial_number, self.quantity, self.storage_guid, self.transport_guid, self.currency, self.price)

class FactoryStockFromPlanFactEvent(object):
    @classmethod
    def create(cls, plan_fact_events):
        """
        создает словари по событиям перемещений продуктов.
        """
        if not cls.__is_allow_quantity_for_stock_with_serial_number(plan_fact_events.quantity):
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
    def __is_allow_quantity_for_stock_with_serial_number(cls, quantity):
        if not quantity == 1:
            return False
        return True

class FactoryStockFromParams(object):
    @classmethod
    def create(cls, product_guid, serial_number, quantity, currency, price):
        """
        создает словари по событиям перемещений продуктов.
        """
        if not cls.__is_allow_quantity_for_stock_with_serial_number(quantity):
            # серийные товары всегда в колличестве 1
            assert False
        return (
            product_guid,
            serial_number,
            quantity,
            currency,
            price,
        )

    @classmethod
    def __is_allow_quantity_for_stock_with_serial_number(cls, quantity):
        if not quantity == 1:
            return False
        return True

class FacrtoryProductGuidWithQuantity(object):
    """
    Сколько каких товаров нужно
    """
    @classmethod
    def create(cls, basket):
        elements = []
        for item in basket():
            elements.append(
                (
                    product_guid,
                    quantity,
                )
            )
        return elements

class ServiceTransferProductFromTo(object):
    """
    Будет ли обект данного класа следить о целостности всех инвариантов?
        можно использовать два клааса один с отслеживанием другой без.
        Отслеживать можно что товар нелдьзя списато до того как зачислить,
            При таком подходе отирцательные остатки не возможны.
    """

    def all_storage_guids(self):
        return PlanFactEvent.storage_guids()

    def chains_storage_delivery_from_storage_to_storage(self, storage_guid, storage_pickup_guid):
        return []

    def datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(self, transport_guid, storage_guid_depart, storage_guid_arrival, datetime_depart):
        return []

    def datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(self, transport_guid, storage_guid_depart, storage_guid_arrival, datetime_start, datetime_pickup):
        return []

    def edge_transport_delivery_from_storage_to_storage_in_datetime_range(self, transport_guid, storage_guid_depart, storage_guid_arrival, datetime_start, datetime_pickup):
        items_edge_delivery = []
        datetimes_depart = self.service_transfer.datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(\
            transport_guid, storage_guid_depart, storage_guid_arrival, datetime_start, datetime_pickup)
        for datetime_depart in datetimes_depart:
            datetimes_arrival = self.service_transfer.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(\
                transport_guid, storage_guid_depart, storage_guid_arrival, datetime_depart)
            for datetime_arrival in datetimes_arrival:
                items_edge_delivery.append(
                    (
                        storage_guid_depart, datetime_depart, transport_guids, storage_guid_arrival, datetime_arrival,
                    )
                )
        return items_edge_delivery

    def edge_delivery(self, storage_guid_depart, storage_guid_arrival, datetime_start, datetime_pickup):
        # Формируем набор перемещений который проходи из с1 в с2 и укладывающийся в нужный времнной диапазон 
        items_edge_delivery = []
        transport_guids = self.service_transfer.transport_guids_delivery_from_storage_to_storage(storage_guid_depart, storage_guid_arrival)
        for transport_guid in transport_guids:
            for item_edge_delivery in self.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_guid, storage_guid_depart, storage_guid_arrival, datetime_start, datetime_pickup):
                items_edge_delivery.append(item_edge_delivery)

        # Если не смогли проехать в по даному участку цепи
        if not items_edge_delivery:
            assert False
        if len(items_edge_delivery) == 0:
            assert False
        return items_edge_delivery

    def fast_chain(self, storage_guid, storage_pickup_guid, transport_guids_allow_for_stock, datetime_start, datetime_pickup):
        chians = []
        for chain_storage_delivery in self.service_transfer.chains_storage_delivery_from_storage_to_storage(storage_guid, storage_pickup_guid):
            items_delivery = []
            for i in range(1,len(chain_storage_delivery)):
                storage_guid_depart = chain_storage_delivery[0]
                storage_guid_arrival = chain_storage_delivery[1]
                items_edge_delivery = self.edge_delivery(storage_guid_depart, storage_guid_arrival, datetime_start, datetime_pickup)
                items_delivery.append(items_edge_delivery)

            # Находим кратчайший маршрут из набора возможных перемещенеий между ребрарами
            fast_chain = []
            currnet_datetime = None
            for item in items_delivery:
                if currnet_datetime:
                    filter(lambda i: i[4] > currnet_datetime, item)
                filter(lambda i: i[2] in transport_guids_allow_for_stock, item)
                if not item:
                    raise False
                sorted(item, key=lambda i: i[4])
                currnet_datetime = item[0][4]
                fast_chain.append(item[0])

            chians.append(fast_chain)

        # разные цепочки сортиуем по дате доставки
        sorted(chians, key=lambda i: i[-1][4])
        very_fast_chain = chians[0]

        return very_fast_chain

    def move(self, product_guid, quantity_for_transfer, storage_depart_guid, datetime_depart, transport_guid, storage_arrival_guid, datetime_arrival):
        #Получить столько информаци по имеющимся сейчас релальным товарам на складе чтобы потом их же списать, транспортировать и принять уже на другом.
        # транзакция с локом на чтение конкртеных записей, нужна для того чтобы при вытаскиваннии из событий того что приняли и хотим сейчас перевести. 
        #  Не встрял другой конкурирующий процес и не увез товары под другое перемещение.
        #   Если такое произойдет то в двух накладных на списание может фигурировать товар с одим и темже серийником.

        #start transaction
        #получить сейрийники подходящих товаров
        #stocks_ready_for_move = PlanFactEvent.stocks_ready_for_move(storage_depart_guid, product_guid)
        stocks_ready_for_move = self.stocks_ready_for_move(storage_depart_guid, product_guid)

        #выбрать столько сколько нужно.
        if len(stocks_ready_for_move) < quantity_for_transfer:
            print 'Error: Has not stocks nead. In stock %s nead stock %s' % (len(stocks_ready_for_move), quantity_for_transfer)
            assert False
        stocks = stocks_ready_for_move[:quantity_for_transfer]
        #залочить их для других перемещений
        #    если не получилось залочить получить другие без этих
        #списать их с склада
        for stock in stocks:
            self.__pull_stock(datetime_depart, storage_depart_guid, stock)
        #снять блокировку
        #принять их к перемещению
        for stock in stocks:
            PlanFactEvent.push_transfer(datetime_depart, transport_guid, stock)
        #списать их с перемещения
        for stock in stocks:
            PlanFactEvent.pull_transfer(datetime_arrival, transport_guid, stock)
        #приянть их на складе получателе
        for stock in stocks:
            self.__push_stock(datetime_arrival, storage_arrival_guid, stock)
        #finish transaction

    def pull(self, datetime_process, storage_guid, product_guid, serial_number, quantity, currency, price):
        """
        Данный сепрвис не просто забирает с склада товар, а он еще и проверяем достаточно ли его.
            А точно он долже быть частью работы по сохраннию событий?
            Возможно события просто надо уметь сохранять. Не зависимо от текущего состояния.
                Потому что это лишь модель и ее нельзя быть уверенным что она с рельностью не разехалсь.
        """
        #stock = PlanFactEvent.create_stock_with_serial_number_v2(product_guid, serial_number, quantity, currency, price)
        stock = FactoryStockFromParams().create(product_guid, serial_number, quantity, currency, price)
        self.__pull_stock(datetime_process, storage_guid, stock)

    def __pull_stock(self, datetime_process, storage_guid, stock):
        plan_fact_event = PlanFactEvent.objects.create(
            datetime_process = datetime_process,
            storage_guid = storage_guid,
            product_guid = stock[0],
            serial_number = stock[1],
            quantity = stock[2],
            currency = stock[3],
            price = stock[4],
            is_in = False,
            is_out = True,
            is_plan = False,
            is_fact = True)

    def push(self, datetime_process, storage_guid, product_guid, serial_number, quantity, currency, price):
        #stock = PlanFactEvent.create_stock_with_serial_number_v2(product_guid, serial_number, quantity, currency, price)
        stock = FactoryStockFromParams().create(product_guid, serial_number, quantity, currency, price)
        self.__push_stock(datetime_process, storage_guid, stock)

    def __push_stock(self, datetime_process, storage_guid, stock):
        plan_fact_event = PlanFactEvent.objects.create(
            datetime_process = datetime_process,
            storage_guid = storage_guid,
            product_guid = stock[0],
            serial_number = stock[1],
            quantity = stock[2],
            currency = stock[3],
            price = stock[4],
            is_in = True,
            is_out = False,
            is_plan = False,
            is_fact = True)

    def stocks_ready_for_move(self, storage_guid, product_guid):
        """
        Простое перемещенеи между складами организации, поэтому изменния цены ен происходит.
        В дальнейшем можно будет проводить оперцию по изменрию цены при порче позиции при транспортировке или ...

        Только для товаров с серийниками.
        """
        stocks = []
        for plan_fact_event in PlanFactEvent.list_for_fact_storage_guid_product_guid_sort_by_datetime_process(storage_guid, product_guid):
            stock = FactoryStockFromPlanFactEvent().create(plan_fact_event)
            if stock in stocks:
                if plan_fact_event.is_push():
                    assert False
                elif plan_fact_event.is_pull():
                    stocks.remove(stock)
                else:
                    assert False
            else:
                if plan_fact_event.is_push():
                    stocks.append(stock)
                elif plan_fact_event.is_pull():
                    assert False
                else:
                    assert False
        return list(stocks)


class ServiceOrder(object):
    """
    Сервис будет создавать заказы.
        В дальнешем еще перемезения для их обеспечения.

        Чтобы создать заказ клиента на покупку телефона и чтобы он приехал на pickup point для его получения 23.09.2018 нужно:
        1) просчитать - проверить что мы можем доставить на эту точку телефон.
        2) сформировать план по перемещению телефона на эту точку
        3) сформировать план на получить деньги от клиента.
        4) сформировать план на выдачу клиенту и смену владельца товара.
        5) далее в процессе будут появляться документы подтверждающие действия по плану.

        datetime_pricess - время совершения операции.
        а время формирования документа можно смотреть в документах.
        у плановых операций есть время когда они должны быть дективированы. План на год? или не надо так делать?
        но время когда плановое децствие отменяется перестает "существовать" оно или удаляется, но тогда предыдущие данные изменятся или нужно чтобы окончилось и сразу появился  в замен новый план. Или не появился.
        Как учесть что заланировано и не сделано от того что запланировано но поменялось?
    """

    def __list_stocks_for_basket(self, basket):
        stocks = []
        # Получили остатки нужных товаров от всех складов
        for item in basket:
            product_guid = item.get_product_guid()
            for storage_guid in self.__service_transfer.all_storage_guids():
                for stock in self.__service_transfer.stocks_ready_for_move(storage_guid, product_guid):
                    stocks.append(stock)
        return stocks

    #def __generate_plan_event_for_delivery_product_guids_with_quantity_to_client(self, product_guids_with_quantity, basket, storage_pickup_guid, datetime_start, datetime_pickup):
    def __generate_plan_event_for_delivery_basket_to_client(self, basket, storage_pickup_guid, datetime_start, datetime_pickup):
        #stocks = self.__list_stocks_for_basket(basket)

        groups_events_posible_for_product = {}

        for item in basket:
            product_guid = item.get_product_guid()
            groups_events_posible = []
            for storage_guid in self.__service_transfer.all_storage_guids():
                for stock in self.__service_transfer.stocks_ready_for_move(storage_guid, product_guid):
                    transport_guids_allow_for_stock = self.__service_transfer.transport_guids_allow_for_stock(stock)
                    chain = self.__service_transfer.fast_chain(storage_guid, storage_pickup_guid, transport_guids_allow_for_stock, datetime_start, datetime_pickup)

                    #product_guid = stock[0]
                    #quantity_for_transfer = stock[2]
                    #storage_depart_guid = storage_guid
                    #storage_arrival_guid = storage_pickup_guid
                    #for transport_guid in self.__service_transfer.transport_guids_delivery_form_to(storage_guid, storage_pickup_guid)
                    #self.__service_transfer.move(product_guid, quantity_for_transfer, storage_depart_guid, datetime_depart, transport_guid, storage_pickup_guid, datetime_arrival):

        plan_events = []
        return plan_events

    def __has_basket_on_stocks(self, basket):
        #stocks = []
        ## Получили остатки нужных товаров от всех складов
        #for item in basket:
        #    product_guid = item.get_product_guid()
        #    for storage_guid in self.__service_transfer.all_storage_guids():
        #        for stock in self.__service_transfer.stocks_ready_for_move(storage_guid, product_guid):
        #            stocks.append(stock)
        stocks = self.__list_stocks_for_basket(basket)

        # Протверили что все что указано в корзине есть на каких то складах в данный момент времни.
        #  Разбираем случай когда stock - это один серийный товар
        for item in basket:
            product_guid = item.get_product_guid()
            for i in range(0, item.get_quantity()):
                temp_stock = None
                for stock in stocks:
                    if stock[0] == product_guid:
                        temp_stock = stock
                        break
                else:
                    # Не нашли на остатках товар из корзины
                    return False
                stocks.remove(temp_stock)
        return True

    def __init__(self, service_transfer):
        self.__service_transfer = service_transfer

    def __is_delivery(self, basket):
        return True

    def create_order_sale_pickup(self, basket, storage_pickup_guid, datetime_start, datetime_pickup):
        if self.__has_basket_on_stocks(basket) and self.__is_delivery(basket):

            #product_guids_with_quantity = FacrtoryProductGuidWithQuantityFromBasket().create(basket)
            #plan_events = self.__generate_plan_event_for_delivery_product_guids_with_quantity_to_client(product_guids_with_quantity, basket, storage_pickup_guid, datetime_pickup)
            plan_events = self.__generate_plan_event_for_delivery_basket_to_client(basket, storage_pickup_guid, datetime_start, datetime_pickup)
            pass


