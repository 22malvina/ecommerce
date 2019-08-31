#!-*-coding: utf-8 -*-
from django.test import TestCase

from planfactevent.models import *
from django.test.client import Client
import json
import sys
import time
import pprint
from decimal import Decimal
from django.utils import timezone
import datetime
import pytz

class TestEStorage(TestCase):
    def setUp(self):
        print("SETUP DATA FOR ...")
        self.assertEqual.__self__.maxDiff = None

    def test_base_1(self):
        datetime_process = timezone.now()
        self.assertEqual(0, PlanFactEvent.count_product([], []))

        storage_guid_1 = 1

        product_guid_mi8 = 1

        # Закупка пратии Mi8
        quantity_mi8 = 10
        purchase_cost_mi8 = 105.1
        currency_mi8 = "USD"

        plan_fact_event_1 = PlanFactEvent.objects.create(storage_guid=storage_guid_1, product_guid=product_guid_mi8, quantity=quantity_mi8, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)

        quantity = PlanFactEvent.count_product([storage_guid_1], [product_guid_mi8])
        self.assertEqual(10, quantity)
        # закупка прошла успешно

        storage_guid_2 = 2

        # Закупка пратии Mi8 на склад 2
        quantity_mi8_2_1 = 8
        purchase_cost_mi8_2_1 = 105.1
        currency_mi8_2_1 = "USD"

        plan_fact_event_2 = PlanFactEvent.objects.create(storage_guid=storage_guid_2, product_guid=product_guid_mi8, quantity=quantity_mi8_2_1, currency=currency_mi8_2_1, price=purchase_cost_mi8_2_1, is_in=True, is_out=False, is_plan=False, is_fact=True)

        quantity = PlanFactEvent.count_product([storage_guid_2], [product_guid_mi8])
        self.assertEqual(8, quantity)
        # закупка прошла успешно

        # Всего продуктов в системе
        self.assertEqual(18, PlanFactEvent.count_product([], []))

        product_guid_r = 2

        # Закупка пратии r
        quantity_r = 5
        purchase_cost_r = 80
        currency_r = "USD"
        plan_fact_event_3 = PlanFactEvent.objects.create(storage_guid=storage_guid_1, product_guid=product_guid_r, quantity=quantity_r, currency=currency_r, price=purchase_cost_r, is_in=True, is_out=False, is_plan=False, is_fact=True)
        quantity = PlanFactEvent.count_product([storage_guid_1], [product_guid_r])
        self.assertEqual(5, quantity)
        # закупка прошла успешно

        self.assertEqual(15, PlanFactEvent.count_product([storage_guid_1], []))

        # Через несколько дней планируя высокий обем спроса на Ми8, закупили еще Mi8 но по чуть большей цене
        quantity_mi8_2 = 20
        purchase_cost_mi8_2 = 120
        currency_mi8_2 = "USD"
        plan_fact_event_4 = PlanFactEvent.objects.create(storage_guid=storage_guid_1, product_guid=product_guid_mi8, quantity=quantity_mi8_2, currency=currency_mi8_2, price=purchase_cost_mi8_2, is_in=True, is_out=False, is_plan=False, is_fact=True)
        quantity = PlanFactEvent.count_product([storage_guid_1], [product_guid_mi8])
        # с учетом предыдущих 10 ми8 суммарно получили 30
        self.assertEqual(30, quantity)
        # закупка прошла успешно

        self.assertEqual(35, PlanFactEvent.count_product([storage_guid_1], []))

        big_quantity = 1000
        # Так как это факты и планы то если мы можем в будущем спрсиать больше чем есть и по факту списать больше чем в системе.
        #  поэтому даныый кейс не имеет смысла.
        # Выбрасывается исключение так как пытаемся списать товара больше чем есть вналичии
        #self.assertRaises(AssertionError, storage_1.pull, product_mi8, big_quantity)

        quantity_mi8_3 = 4
        plan_fact_event_5 = PlanFactEvent.objects.create(storage_guid=storage_guid_1, product_guid=product_guid_mi8, quantity=quantity_mi8_3, currency=currency_mi8_2, price=purchase_cost_mi8_2, is_in=False, is_out=True, is_plan=False, is_fact=True)
        quantity = PlanFactEvent.count_product([storage_guid_1], [product_guid_mi8])
        self.assertEqual(26, quantity)
        self.assertEqual(31, PlanFactEvent.count_product([storage_guid_1], []))
        # Всего продуктов в системе
        self.assertEqual(39, PlanFactEvent.count_product([], []))
        # Всего mi8 в системе
        self.assertEqual(34, PlanFactEvent.count_product([], [product_guid_mi8]))
        # Всего r в системе
        self.assertEqual(5, PlanFactEvent.count_product([], [product_guid_r]))

        # проверка push_stocks
        quantity_mi8_4 = 5
        plan_fact_event_5 = PlanFactEvent.push_stocks(datetime_process, storage_guid_1, product_guid_mi8, quantity_mi8_4, currency_mi8_2, purchase_cost_mi8_2)
        quantity = PlanFactEvent.count_product([storage_guid_1], [product_guid_mi8])
        self.assertEqual(31, quantity)
        self.assertEqual(36, PlanFactEvent.count_product([storage_guid_1], []))
        # Всего продуктов в системе
        self.assertEqual(44, PlanFactEvent.count_product([], []))
        # Всего mi8 в системе
        self.assertEqual(39, PlanFactEvent.count_product([], [product_guid_mi8]))
        # Всего r в системе
        self.assertEqual(5, PlanFactEvent.count_product([], [product_guid_r]))

        # проверка pull_stocks
        quantity_r = 2
        plan_fact_event_5 = PlanFactEvent.pull_stocks(datetime_process, storage_guid_2, product_guid_r, quantity_r, currency_r, purchase_cost_r)
        quantity = PlanFactEvent.count_product([storage_guid_1], [product_guid_mi8])
        self.assertEqual(31, quantity)
        self.assertEqual(36, PlanFactEvent.count_product([storage_guid_1], []))
        # Всего продуктов в системе
        self.assertEqual(42, PlanFactEvent.count_product([], []))
        # Всего mi8 в системе
        self.assertEqual(39, PlanFactEvent.count_product([], [product_guid_mi8]))
        # Всего r в системе
        self.assertEqual(3, PlanFactEvent.count_product([], [product_guid_r]))


    def test_transfer(self):
        #datetime_process = timezone.now()
        self.assertEqual(0, PlanFactEvent.count_product([], []))
        self.assertEqual(0, PlanFactEvent.count_product_with_serial_number([], []))

        service_transfer = ServiceTransferProductFromTo()

        storage_depart_guid = 1
        storage_arrival_guid = 2
        product_guid_mi8 = 1

        quantity_mi8 = 10
        purchase_cost_mi8 = 105.1
        currency_mi8 = "USD"

        datetime_process = datetime.datetime(2001, 1, 1, 12, 30, 00, tzinfo=pytz.UTC)

        #for i in range(0, quantity_mi8):
        #    plan_fact_event = PlanFactEvent.objects.create(storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1000 + i, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1001, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1002, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1003, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1004, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1005, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1006, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1007, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1008, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1009, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1010, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        self.assertEqual(10, PlanFactEvent.count_product([storage_depart_guid], [product_guid_mi8]))
        self.assertEqual(10, PlanFactEvent.count_product_with_serial_number([storage_depart_guid], [product_guid_mi8]))
        self.assertEqual(0, PlanFactEvent.count_product([storage_arrival_guid], [product_guid_mi8]))
        self.assertEqual(0, PlanFactEvent.count_product_with_serial_number([storage_arrival_guid], [product_guid_mi8]))

        quantity_for_transfer = 3
        transport_guid = 1
        #datetime_depart = timezone.now() #XXX
        #datetime_arrival = timezone.now() #XXX
        datetime_depart = datetime.datetime(2019, 8, 1, 9, 15, 00, tzinfo=pytz.UTC)
        datetime_arrival = datetime.datetime(2019, 8, 5, 14, 30, 00, tzinfo=pytz.UTC)
        service_transfer.move(product_guid_mi8, quantity_for_transfer, storage_depart_guid, datetime_depart, transport_guid, storage_arrival_guid, datetime_arrival)

        self.assertEqual(7, PlanFactEvent.count_product([storage_depart_guid], [product_guid_mi8]))
        self.assertEqual(7, PlanFactEvent.count_product_with_serial_number([storage_depart_guid], [product_guid_mi8]))
        self.assertEqual(3, PlanFactEvent.count_product([storage_arrival_guid], [product_guid_mi8]))
        self.assertEqual(3, PlanFactEvent.count_product_with_serial_number([storage_arrival_guid], [product_guid_mi8]))

        purchase_cost_mi8 = 124.1
        datetime_process = datetime.datetime(2000, 2, 22, 12, 30, 00, tzinfo=pytz.UTC)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1011, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1012, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1013, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_depart_guid, product_guid=product_guid_mi8, serial_number=1014, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)

        self.assertEqual(11, PlanFactEvent.count_product([storage_depart_guid], [product_guid_mi8]))
        self.assertEqual(11, PlanFactEvent.count_product_with_serial_number([storage_depart_guid], [product_guid_mi8]))
        self.assertEqual(3, PlanFactEvent.count_product([storage_arrival_guid], [product_guid_mi8]))
        self.assertEqual(3, PlanFactEvent.count_product_with_serial_number([storage_arrival_guid], [product_guid_mi8]))

        quantity_for_transfer = 10
        datetime_depart = datetime.datetime(2019, 8, 6, 9, 15, 00, tzinfo=pytz.UTC)
        datetime_arrival = datetime.datetime(2019, 8, 11, 14, 30, 00, tzinfo=pytz.UTC)
        service_transfer.move(product_guid_mi8, quantity_for_transfer, storage_depart_guid, datetime_depart, transport_guid, storage_arrival_guid, datetime_arrival)

        self.assertEqual(1, PlanFactEvent.count_product([storage_depart_guid], [product_guid_mi8]))
        self.assertEqual(1, PlanFactEvent.count_product_with_serial_number([storage_depart_guid], [product_guid_mi8]))
        self.assertEqual(13, PlanFactEvent.count_product([storage_arrival_guid], [product_guid_mi8]))
        self.assertEqual(13, PlanFactEvent.count_product_with_serial_number([storage_arrival_guid], [product_guid_mi8]))

        quantity_for_transfer = 5
        datetime_depart = datetime.datetime(2019, 8, 6, 9, 15, 00, tzinfo=pytz.UTC)
        datetime_arrival = datetime.datetime(2019, 8, 11, 14, 30, 00, tzinfo=pytz.UTC)
        self.assertRaises(AssertionError, service_transfer.move, product_guid_mi8, quantity_for_transfer, storage_depart_guid, datetime_depart, transport_guid, storage_arrival_guid, datetime_arrival)

        ## Проверяем работу когда меньше 0, и когда сначало появились отрицательные остатки
        serial_number = 1012
        quantity_pull = 1
        storage_guid_1 = 101
        self.assertEqual(0, PlanFactEvent.count_product_with_serial_number([storage_guid_1], [product_guid_mi8]))
        datetime_process = datetime.datetime(2019, 7, 7, 9, 02, 00, tzinfo=pytz.UTC)
        service_transfer.push(datetime_process, storage_guid_1, product_guid_mi8, serial_number, quantity_pull, currency_mi8, purchase_cost_mi8)
        self.assertEqual(1, PlanFactEvent.count_product_with_serial_number([storage_guid_1], [product_guid_mi8]))

        datetime_process = datetime.datetime(2019, 7, 7, 9, 01, 00, tzinfo=pytz.UTC)
        service_transfer.pull(datetime_process, storage_guid_1, product_guid_mi8, serial_number, quantity_pull, currency_mi8, purchase_cost_mi8)
        self.assertEqual(0, PlanFactEvent.count_product([storage_guid_1], [product_guid_mi8]))
        #self.assertEqual(0, PlanFactEvent.count_product_with_serial_number([storage_guid_1], [product_guid_mi8]))
        # получается что сприсали раньше чем добавили
        self.assertRaises(AssertionError, PlanFactEvent.count_product_with_serial_number, [storage_guid_1], [product_guid_mi8])

        datetime_process = datetime.datetime(2019, 7, 7, 9, 03, 00, tzinfo=pytz.UTC)
        service_transfer.pull(datetime_process, storage_guid_1, product_guid_mi8, serial_number, quantity_pull, currency_mi8, purchase_cost_mi8)
        # отрицательный остаток получился
        self.assertRaises(AssertionError, PlanFactEvent.count_product, [storage_guid_1], [product_guid_mi8])
        self.assertRaises(AssertionError, PlanFactEvent.count_product_with_serial_number, [storage_guid_1], [product_guid_mi8])

        datetime_process = datetime.datetime(2019, 7, 7, 9, 00, 00, tzinfo=pytz.UTC)
        service_transfer.push(datetime_process, storage_guid_1, product_guid_mi8, serial_number, quantity_pull, currency_mi8, purchase_cost_mi8)
        self.assertEqual(0, PlanFactEvent.count_product([storage_guid_1], [product_guid_mi8]))
        self.assertEqual(0, PlanFactEvent.count_product_with_serial_number([storage_guid_1], [product_guid_mi8]))

        datetime_process = datetime.datetime(2019, 7, 7, 9, 02, 45, tzinfo=pytz.UTC)
        service_transfer.push(datetime_process, storage_guid_1, product_guid_mi8, serial_number, quantity_pull, currency_mi8, purchase_cost_mi8)
        self.assertEqual(1, PlanFactEvent.count_product([storage_guid_1], [product_guid_mi8]))
        #self.assertEqual(1, PlanFactEvent.count_product_with_serial_number([storage_guid_1], [product_guid_mi8]))
        # так как одновремменно на один склад добавили дважды товар с одиним серийным номером
        self.assertRaises(AssertionError, PlanFactEvent.count_product_with_serial_number, [storage_guid_1], [product_guid_mi8])

        for e in PlanFactEvent.objects.all():
            print e

    def test_create_order_sale_pickup_1(self):
        """
        Доставка на продукт 1 (телефон Mi8) клиенту 1 на точку получения 3 с склада 1(один из наших поставщиков) через наш промежуточный склад 2.
        У компании есть транспортное средство 1 (грузовик) ездит 1 раз в день междк складами 1 и 2.
        А также 2 (автомобиль) которые ездит с 2 на 3.
        Оба перевозят грузы любых размеров.
        Пользователь оформил заказ на сайте 2019, 7, 1, 12, 15, 46.
        А из передложенных дат получения выбрал 2019, 7, 7, 9, 13, 00.

        Задача сразу после создания заказа, у нас в системе, содать план действий по его реализации.
        Пример плана по движению товара:
            2019, 7, 1, 16, 00, 00 отгрузка у поставщика с склада 1
            2019, 7, 1, 16, 00, 00 грузковик 1 принял к перемещению заказ
            2019, 7, 1, 19, 00, 00 грузковик 1 отгрузил закза
            2019, 7, 1, 19, 00, 00 склад 2 принял на зхарание заказ
            2019, 7, 2, 10, 00, 00 склад 2 отгрузил заказ
            2019, 7, 2, 10, 00, 00 автомобиль 2 приянл заказ к перемещению
            2019, 7, 2, 11, 00, 00 автомобиль 2 отгрузил закза
            2019, 7, 2, 11, 00, 00 склад 3 принял на харание заказ
            2019, 7, 7,  9, 13, 00 склад 3 отгрузил заказ клиенту 1
            2019, 7, 7,  9, 13, 00 клиенту 1 принял заказ
        План надо расширить движением денежных средств.
            ...

        """
        service_transfer = ServiceTransferProductFromTo()
        service_order = ServiceOrder(service_transfer)
        #service_order.create_order_sale_pickup(cargo, )
        basket_1 = []
        storage_donor_guid_1 = 1
        storage_guid_2 = 2
        storage_pickup_guid_3 = 3
        datetime_create_order = datetime.datetime(2019, 7, 1, 12, 15, 46, tzinfo=pytz.UTC)
        datetime_pickup = datetime.datetime(2019, 7, 7, 9, 13, 00, tzinfo=pytz.UTC)

        service_order.create_order_sale_pickup(basket_1, storage_pickup_guid_3, datetime_create_order, datetime_pickup)

