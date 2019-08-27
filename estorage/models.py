#!-*-coding: utf-8 -*-
from django.db import models
from eproduct.models import *
from epartnumber.models import *

from planfactevent.models import *
import datetime
from django.utils import timezone

#### Region

class Region(models.Model):
    title = models.CharField(max_length=200)

#### City

class City(models.Model):
    title = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

class FilterCityIdRegion(models.Model):
    pickup_points = models.ManyToManyField(City)
    regions = models.ManyToManyField(Region)

#### Storage

class Storage(models.Model):
    """
    API
    """
    title = models.CharField(max_length=200)
    size = models.IntegerField(u"Максимальное количество штук различных позиций, которое может принять склад.")

    def __has(self, product, quantity):
        if self.quantity(product) >= quantity:
            return True
        return False

    def __has_free_place(self, product, quantity):
        if self.quantity_all() + quantity < self.size:
            return True
        return False

    def list_product(self):
        products = set()
        #for stock in Stock.objects.filter(storage=self):
        #    products.add(stock.product)
        #return list(products)
        return list(Product.objects.filter(id__in=PlanFactEvent.product_guids_by_storage_guids([self.id])))

    def list_part_number_for_product(self, product):
        part_numbers = set()
        #for stock in Stock.objects.filter(storage=self, product=product):
        for stock in self.__stocks(product):
            part_numbers.add(stock.part_number)
        return list(part_numbers)

    def __load(self, has, product, quantity, part_number):
        #stock = Stock(product=product, quantity=quantity, storage=self, part_number=part_number, has=has)
        #stock.save()
        #datetime_process = datetime.datetime.now()
        datetime_process = timezone.now()
        if has:
            PlanFactEvent.push_stocks(datetime_process, self.id, product.id, quantity, 'not', 0)
        else:
            PlanFactEvent.pull_stocks(datetime_process, self.id, product.id, quantity, 'not', 0)

    def pull(self, product, quantity):
        if not self.__has(product, quantity):
            assert False
        ##cargo = []

        ## Сформировать обеспеченные остатки
        ## Удалять уже из обеспеченных

        ##stocks = []
        ##for stock in Stock.objects.filter(storage=self, product=product, has=True):
        ##    for stock_element in stocks:
        ##        if stock.part_number == stock_element['part_number']:
        ##            stock_element['quantity'] += stock.quantity
        ##            break
        ##    else:
        ##        stocks.append({
        ##            'part_number': stock.part_number,
        ##            'quantity': stock.quantity,
        ##        })

        ##for stock in Stock.objects.filter(storage=self, product=product, has=False):
        ##    for stock_element in stocks:
        ##        if stock.part_number == stock_element['part_number']:
        ##            stock_element['quantity'] -= stock.quantity
        ##            break
        ##    else:
        ##        # Списали того чего не было
        ##        assert False


        ##for stock in stocks:
        ##    if quantity >= stock.quantity:
        ##        unload_quantity = stock.quantity
        ##    else:
        ##        unload_quantity = quantity
        ##    #self.__unload(stock, unload_quantity)
        ##    #XXX Тут ошибка и тесты должны ее выявить
        ##    #self.__load(False, stock.product, quantity, stock.part_number)
        ##    self.__load(False, stock.product, unload_quantity, stock.part_number)
        ##    quantity -= unload_quantity
        ##    #cargo.append({
        ##    #    'product': product,
        ##    #    'quantity': quantity,
        ##    #})
        ##    if quantity == 0:
        ##        break
        ##    elif quantity < 0:
        ##        assert False
        ##for stock in stocks:
        ##    if quantity >= stock['quantity']:
        ##        unload_quantity = stock['quantity']
        ##    else:
        ##        unload_quantity = quantity
        ##    self.__load(False, product, unload_quantity, stock['part_number'])
        ##    quantity -= unload_quantity
        ##    if quantity == 0:
        ##        break
        ##    elif quantity < 0:
        ##        assert False
        #stocks = self.__stocks(product)
        #for stock in stocks:
        #    if quantity >= stock.quantity:
        #        unload_quantity = stock.quantity
        #    else:
        #        unload_quantity = quantity
        #    self.__load(False, product, unload_quantity, stock.part_number)
        #    quantity -= unload_quantity
        #    if quantity == 0:
        #        break
        #    elif quantity < 0:
        #        assert False

        #if quantity > 0:
        #    assert False


        ####
        datetime_process = timezone.now()
        PlanFactEvent.pull_stocks(datetime_process, self.id, product.id, quantity, 'not', 0)
        ####
        #stocks = self.__stocks(product)
        #for stock in stocks:
        #    if quantity >= stock.quantity:
        #        unload_quantity = stock.quantity
        #    else:
        #        unload_quantity = quantity
        #    self.__load(False, product, unload_quantity, stock.part_number)
        #    quantity -= unload_quantity
        #    if quantity == 0:
        #        break
        #    elif quantity < 0:
        #        assert False

        #if quantity > 0:
        #    assert False
 

    def push(self, product, quantity, part_number):
        #TODO проверить есть ли свободное место на складе чтобы принять такой обем груза
        if not self.__has_free_place(product, quantity):
            assert False
        self.__load(True, product, quantity, part_number)

    def quantity(self, product):
        #quantity = 0
        ##for stock in Stock.objects.filter(storage=self, product=product):
        ##    #quantity += stock.quantity
        ##    if stock.has:
        ##        quantity += stock.quantity
        ##    else:
        ##        quantity -= stock.quantity
        #for stock in self.__stocks(product):
        #    quantity += stock.quantity
        #return quantity
        return PlanFactEvent.count_product([self.id], [product.id])

    def quantity_all(self):
        #quantity = 0
        #for stock in Stock.objects.filter(storage=self):
        #    #quantity += stock.quantity
        #    if stock.has:
        #        #print quantity, '+=', stock.quantity
        #        quantity += stock.quantity
        #        #print quantity
        #    else:
        #        #print quantity, '-=', stock.quantity
        #        quantity -= stock.quantity
        #        #print quantity
        #return quantity
        return PlanFactEvent.count_product([self.id], [])

    def __stocks(self, product):
        return Stock.list(self, product)

    #def __unload(self, stock, quantity):
    #    self.__load(False, stock.product, quantity, stock.part_number)


class Stock(models.Model):
    """
        Система учета товара движения, между ответсвенными объектами.
            позволит ответить кто когда куда сколько принял\выдал.

        Пока не учитывабются габариты продуктов принимаемых на склад можно работать с product_guid.
        Когда габариты станут частью просчета, возможности принятия на склад и размещения на нем, то это станет частью даного ограниченного контекста,
            но всеравно не будет частью агрегата склад.

        При размещении товара на складе важно учитывать размер?
        На складе есть адресно храние - стойка, ряд, место?
        Название, цвет, разрешение экрана, мощность - не важны?
        Нужно ли иметь поиск товаров по складу?
            по артикулу?
            по продукту?
            по партии?
            по поставщику?
        Нужен ли паспорт продукта?
            где будеть храниться паспорт продукта?
        На какие вопросы по продукту хотим ответить?
            как и от кого пришел в систему?
            по какой цене пришел в систему?
            какие перемещения осуществлялись?
            где сейчас находится?
            куда движется?

        Вводить принудительный серийный номер, тогда точно будем знать на что поставлен резерв, и что перемещаем.

    """
    #артикул + количество + номер партии + серийник + поставщик + цена закупки = груз
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    article = models.CharField(u'Артикул продукта', max_length=200, null=True, blank=True)
    part_number = models.ForeignKey(PartNumber, on_delete=models.CASCADE)
    serial_number = models.CharField(u'Серийны номер/как персона', max_length=200, null=True, blank=True)
    price_purchase = models.DecimalField(u"стоимость покупки одной штуки", decimal_places=2, max_digits=7, null=True, blank=True)
    supplier = models.CharField(u'Поставщик', max_length=200, null=True, blank=True)
    quantity = models.IntegerField(u"Количество")

    invoice_guid = models.CharField(u'GUID накладной', max_length=200, null=True, blank=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    # общая система остатков между складами и транспортными средствами
    #transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    has = models.BooleanField(verbose_name=u'Пришоло на склад / ушло с склада', default=True)
    datetime_create = models.DateTimeField(u'дата и время создание', auto_now_add=True)
    datetime_process = models.DateTimeField(u'дата и время проведения опрерации', null=True, blank=True)

    @staticmethod
    def list(storage, product):
        stocks = []
        for stock in Stock.objects.filter(storage=storage, product=product, has=True):
            for stock_element in stocks:
                if stock.part_number == stock_element['part_number']:
                    stock_element['quantity'] += stock.quantity
                    break
            else:
                stocks.append({
                    'part_number': stock.part_number,
                    'quantity': stock.quantity,
                })

        for stock in Stock.objects.filter(storage=storage, product=product, has=False):
            for stock_element in stocks:
                if stock.part_number == stock_element['part_number']:
                    stock_element['quantity'] -= stock.quantity
                    break
            else:
                # Списали того чего не было
                assert False

        stock_object = []
        for stock in stocks:
            if stock['quantity'] < 0:
                assert False
            elif stock['quantity'] > 0:
                stock_object.append(Stock(product=product, quantity=stock['quantity'], storage=storage, part_number=stock['part_number'], has=True))
        return stock_object

    def list_all():
        pass


class FilterStorageId(models.Model):
    storages = models.ManyToManyField(Storage)

#### PickupPoint

class PickupPoint(models.Model):
    """
    API
    """
    title = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def get_city(self):
        return self.city

    def is_null(self):
        return False

class FilterPickupPointIdCity(models.Model):
    pickup_points = models.ManyToManyField(PickupPoint)
    cities = models.ManyToManyField(City)

#### System Warehouse - Service

#
#product_spec_storage = FactoryProductSpecStorage.create(Product)
#   длина
#   высота
#   ширна
#   вес
#   хрупкое
#   жидкое
#   взрывчатое

class SystemWarehouse(models.Model):
    """
    API
    С данной системой следует общаться GUID складов, продуктов, ...

    Хотим знать где лежит продукт с опредеелнным :
        серийным номером ?
        артикулом ?
        из опеределенной пратии ?
    """
    storages = models.ManyToManyField(Storage)

    def pull(self, storage, product, quantity):
        storage.pull(product, quantity)

    def pull_cargo(self, storage, cargo):
        for product, quantiry in cargo.product_quqntity():
            storage.pull(product, quantity)

    #def pull_guid(self, storage_guid, product_guid, quantity):
    #    prdocuct_spec_storage = Product.object.get(id=product_guid)
    #    storage = Storage.object.get(id=storage_guid)
    #    storage.pull(product_spec_storage, quantity)

    def push(self, storage, product, quantity, part_number):
        storage.push(product, quantity, part_number)

    def push_cargo(self, storage, cargo):
        if storage.has_cargo():
            pass
        for product, quantiry, part_number in cargo.product_quqntity_part_number():
            storage.push(product, quantity, part_number)

    #def push_guid(self, storage_guid, product_guid, quantity, part_number):
    #    prdocuct_spec_storage = Product.object.get(id=product_guid)
    #    storage = Storage.object.get(id=storage_guid)
    #    storage.push(product_spec_storage, quantity, part_number)

    def quantity(self, product):
        ## slow
        quantity = 0
        for storage in self.storages:
            quantity += storage.quantity(product)
        ## fast
        stock_object = Stock.list_all(product)
        return quantity


#### Transport
class Transport(models.Model):
    title = models.CharField(max_length=200)
    size = models.IntegerField(u"Максимальное количество штук различных позиций, которое может принять для перевозки транспорт.")

class TripPlan(models.Model):
    """
    Нужна цепочка перемещений
    """
    datetime_arrival = models.DateTimeField(u'дата и время прибытия', null=True, blank=True)
    datetime_create = models.DateTimeField(u'дата и время создание', auto_now_add=True)
    datetime_depart = models.DateTimeField(u'дата и время отпраления', null=True, blank=True)
    storage_arrival = models.ForeignKey(Storage, related_name="trip_plan_storage_arrival")
    storage_depart = models.ForeignKey(Storage, related_name="trip_plan_storage_depart")
    transport = models.ForeignKey(Transport)
    #plan
    #datetime_confirmed_fact = models.DateTimeField(u'дата и время прибытия', null=True, blank=True)
    #fact
    def __init__(self):
        self.__cargo = []

class TripFact(models.Model):
    invoice_guid = models.CharField(u'GUID накладной', max_length=200, null=True, blank=True)
    has = models.BooleanField(verbose_name=u'Принято к перевозке / Выданано по прибытию', default=True)
    transport = models.ForeignKey(Transport)
    #trip_plan = models.ForeignKey(TripPlan)
    datetime_create = models.DateTimeField(u'дата и время создание', auto_now_add=True)
    datetime_process = models.DateTimeField(u'дата и время проведения опрерации', null=True, blank=True)

    def __init__(self):
        self.__cargo = []

class SystemTransfer(models.Model):
    """
    API
    """
    storages = models.ManyToManyField(Storage)
    transport = models.ManyToManyField(Transport)

    def transfer(cargo, storage_depart, storage_arrival):
        """
        В cargo может не содердать серийного номера.
        И всеравно перемещение пройдет нормально так как информация будет локализовна внутри данного ограниченного контекста.

        Что делать с резервами под клиентские заказы, если в них не содержится серийника?
            Надо чтобы система резервирования тоже знала о серийниках.
            Но сначало товар должен встать на остатки а потом его уже можно зарезервировать.
            Пропадет возможность резервировать товар которого еще нет.

        Так как операция растянутая во времени. И мы не можем создать ее разом то, есть решения:
            1. Делать создание на будущее(время публикации)
                И всегда спрашивать события опубликованне до опеределнного момента времени(текущего).
                Получится полноценная система основанная на накоплении событий.
                А чтобы не простичывать каждый раз все события, сделать что то тип инвенторизации.
                    Но только когда данная модельначнет исчерапает себя по производительности.
                    И иметь возмодность запускать механизим инвенторизации по событию.
        """
        pass



