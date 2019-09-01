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

        repository_schedule = RepositorySchedule()
        graph = Graph(repository_schedule)
        service_transfer = ServiceTransferProductFromTo(repository_schedule, graph)

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

        #for e in PlanFactEvent.objects.all():
        #    print e

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

        repository_schedule = RepositorySchedule()
        graph = Graph(repository_schedule)
        service_transfer = ServiceTransferProductFromTo(repository_schedule, graph)
        service_order = ServiceOrder(service_transfer)
        #service_order.create_order_sale_pickup(cargo, )

        product_guid_mi8 = 1
        purchase_cost_mi8 = 105.1
        currency_mi8 = "USD"

        quantity_mi8 = 1
        basket_1 = [(product_guid_mi8, quantity_mi8),]
        storage_donor_guid_1 = 1
        storage_guid_2 = 2
        storage_pickup_guid_3 = 3

        datetime_process = datetime.datetime(2001, 1, 1, 12, 30, 00, tzinfo=pytz.UTC)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_donor_guid_1, product_guid=product_guid_mi8, serial_number=1001, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)
        plan_fact_event = PlanFactEvent.objects.create(datetime_process=datetime_process, storage_guid=storage_donor_guid_1, product_guid=product_guid_mi8, serial_number=1002, quantity=1, currency=currency_mi8, price=purchase_cost_mi8, is_in=True, is_out=False, is_plan=False, is_fact=True)

        service_transfer.add_storage_guid(storage_donor_guid_1)
        service_transfer.add_storage_guid(storage_guid_2)
        service_transfer.add_storage_guid(storage_pickup_guid_3)

        transport_auto_guid_1 = 1
        transport_car_guid_2 = 2

        service_transfer.add_transport_guid(transport_auto_guid_1)
        service_transfer.add_transport_guid(transport_car_guid_2)
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 1, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 1, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 2, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 2, 11, 00, 00, tzinfo=pytz.UTC))

        datetime_create_order = datetime.datetime(2019, 7, 1, 12, 15, 46, tzinfo=pytz.UTC)
        datetime_pickup = datetime.datetime(2019, 7, 7, 9, 13, 00, tzinfo=pytz.UTC)

        self.assertEqual([storage_donor_guid_1, storage_guid_2, storage_pickup_guid_3], service_transfer.all_storage_guids())
        self.assertEqual(
            [(storage_donor_guid_1, storage_guid_2, storage_pickup_guid_3)],
            graph.chain_master(storage_donor_guid_1, storage_pickup_guid_3)
        )
        self.assertEqual(
            [datetime.datetime(2019, 7, 1, 19, 00, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_auto_guid_1, storage_donor_guid_1, storage_guid_2, datetime.datetime(2019, 7, 1, 16, 00, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [datetime.datetime(2019, 7, 2, 11, 00, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_car_guid_2, storage_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 2, 10, 00, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [datetime.datetime(2019, 7, 1, 16, 00, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(transport_auto_guid_1, storage_donor_guid_1, storage_guid_2, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [datetime.datetime(2019, 7, 2, 10, 00, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(transport_car_guid_2, storage_guid_2, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                (
                    1,
                    datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC),
                    1,
                    2,
                    datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_auto_guid_1, storage_donor_guid_1, storage_guid_2, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                (
                    2,
                    datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC),
                    2,
                    3,
                    datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_car_guid_2, storage_guid_2, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )

        self.assertEqual([1,], repository_schedule.transport_guids_delivery_from_storage_to_storage(storage_donor_guid_1, storage_guid_2))
        self.assertEqual(
            [
                (
                    1,
                    datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC),
                    1,
                    2,
                    datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.edge_delivery(storage_donor_guid_1, storage_guid_2, datetime_create_order, datetime_pickup)
        )
        self.assertEqual([2,], repository_schedule.transport_guids_delivery_from_storage_to_storage(storage_guid_2, storage_pickup_guid_3))
        self.assertEqual(
            [
                (
                    2,
                    datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC),
                    2,
                    3,
                    datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.edge_delivery(storage_guid_2, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )
        transport_guids_allow_for_stock = [1,2]
        self.assertEqual(
            [
                (
                    1,
                    datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC),
                    1,
                    2,
                    datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC),
                ),
                (
                    2,
                    datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC),
                    2,
                    3,
                    datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.fast_schedule(storage_donor_guid_1, storage_pickup_guid_3, transport_guids_allow_for_stock, datetime_create_order, datetime_pickup)
        )

        #for plan_fact_event in PlanFactEvent.objects.filter(is_in=True, is_out=False, is_plan=False, is_fact=True):
        for plan_fact_event in PlanFactEvent.objects.all():
            print plan_fact_event
        self.assertEqual(
            [
                (1, 1, 1, datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC)),
                (1, 1, 2, datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC)),
                #(1, 1, 1, datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC)),
                #(1, 1, 2, datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC)),
            ],
            service_order.create_order_sale_pickup(basket_1, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )
        for plan_fact_event in PlanFactEvent.objects.all():
            print plan_fact_event
 
    def test_create_order_sale_pickup_2(self):
        """
        В test_create_order_sale_pickup_1 был приведн пример разарботке на основе TDD(подгоняем реализацию).
        Теперь нужно не подгонять а реализовать реальную логику для анаогичного примера но с другими параметрами.

        Доставка 2-х продуктов (телефон Mi8, чехол) клиенту 2 на точку получения 5 с склада 4(один из наших складов).
        У компании есть транспортное средство 2 (автомобиль) которые ездит с 4 на 5 раз в сутки 14, 30, 00 выезжает и в 16, 00, 00 приезжает.
        Оба перевозят грузы любых размеров.
        Пользователь оформил заказ на сайте 2019, 8, 1, 15, 1, 23.
        А из передложенных дат получения выбрал 2019, 8, 3, 14, 00, 00.

        Задача сразу после создания заказа, у нас в системе, содать план действий по его реализации.
        Пример плана по движению товара:
            2019, 8, 2, 14, 30, 00 отгрузка у поставщика с склада 4
            2019, 8, 2, 14, 30, 00 автомобиль 2 приянл заказ к перемещению
            2019, 8, 2, 16, 00, 00 автомобиль 2 отгрузил закза
            2019, 8, 2, 16, 00, 00 склад 5 принял на зхарание заказ
            2019, 8, 3, 14, 00, 00 склад 5 отгрузил заказ клиенту 1
            2019, 8, 3, 14, 00, 00 клиенту 2 принял заказ
        План надо расширить движением денежных средств.
            ...

        """
        repository_schedule = RepositorySchedule()
        graph = Graph(repository_schedule)
        service_transfer = ServiceTransferProductFromTo(repository_schedule, graph)
        service_order = ServiceOrder(service_transfer)
        basket_1 = []
        storage_guid_4 = 4
        storage_pickup_guid_5 = 5
        service_transfer.add_storage_guid(storage_guid_4)
        service_transfer.add_storage_guid(storage_pickup_guid_5)
        transport_car_guid_2 = 2
        service_transfer.add_transport_guid(transport_car_guid_2)
        #storage_depart_guid, datetime_depart, transport_guid, storage_arrival_guid, datetime_arrival
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 2, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 16, 00, 00, tzinfo=pytz.UTC))

        datetime_create_order = datetime.datetime(2019, 8, 1, 15, 1, 23, tzinfo=pytz.UTC)
        datetime_pickup = datetime.datetime(2019, 8, 3, 14, 00, 00, tzinfo=pytz.UTC)

        self.assertEqual([storage_guid_4, storage_pickup_guid_5], service_transfer.all_storage_guids())
        self.assertEqual(
            [(storage_guid_4, storage_pickup_guid_5)],
            graph.chain_master(storage_guid_4, storage_pickup_guid_5)
        )
        self.assertEqual(
            [datetime.datetime(2019, 8, 2, 16, 00, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_car_guid_2, storage_guid_4, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 14, 30, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [datetime.datetime(2019, 8, 2, 14, 30, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(transport_car_guid_2, storage_guid_4, storage_pickup_guid_5, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                (
                    4,
                    datetime.datetime(2019, 8, 2, 14, 30, tzinfo=pytz.UTC),
                    2,
                    5,
                    datetime.datetime(2019, 8, 2, 16, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_car_guid_2, storage_guid_4, storage_pickup_guid_5, datetime_create_order, datetime_pickup)
        )
        self.assertEqual([2,], repository_schedule.transport_guids_delivery_from_storage_to_storage(storage_guid_4, storage_pickup_guid_5))
        self.assertEqual(
            [
                (
                    4,
                    datetime.datetime(2019, 8, 2, 14, 30, tzinfo=pytz.UTC),
                    2,
                    5,
                    datetime.datetime(2019, 8, 2, 16, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.edge_delivery(storage_guid_4, storage_pickup_guid_5, datetime_create_order, datetime_pickup)
        )
        transport_guids_allow_for_stock = [2]
        self.assertEqual(
            [
                (
                    4,
                    datetime.datetime(2019, 8, 2, 14, 30, tzinfo=pytz.UTC),
                    2,
                    5,
                    datetime.datetime(2019, 8, 2, 16, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.fast_schedule(storage_guid_4, storage_pickup_guid_5, transport_guids_allow_for_stock, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [],
            service_order.create_order_sale_pickup(basket_1, storage_pickup_guid_5, datetime_create_order, datetime_pickup)
        )

    def test_create_order_sale_pickup_3(self):
        """
        Расширим пример test_create_order_sale_pickup_2 добавиви различные виды транспорта и расписания движений.

        Доставка 2-х продуктов (телефон Mi8, чехол) клиенту 2 на точку получения 5 с склада 4(один из наших складов).
        У компании есть транспортное средство 2 (автомобиль) которые ездит с 4 на 5 раз в сутки 14, 30, 00 выезжает и в 16, 00, 00 приезжает.
        Оба перевозят грузы любых размеров.
        Пользователь оформил заказ на сайте 2019, 8, 1, 15, 1, 23.
        А из передложенных дат получения выбрал 2019, 8, 3, 14, 00, 00.

        Задача сразу после создания заказа, у нас в системе, содать план действий по его реализации.
        Пример плана по движению товара:
            2019, 8, 2, 14, 30, 00 отгрузка у поставщика с склада 4
            2019, 8, 2, 14, 30, 00 автомобиль 2 приянл заказ к перемещению
            2019, 8, 2, 16, 00, 00 автомобиль 2 отгрузил закза
            2019, 8, 2, 16, 00, 00 склад 5 принял на зхарание заказ
            2019, 8, 3, 14, 00, 00 склад 5 отгрузил заказ клиенту 1
            2019, 8, 3, 14, 00, 00 клиенту 2 принял заказ
        План надо расширить движением денежных средств.
            ...

        """
        repository_schedule = RepositorySchedule()
        graph = Graph(repository_schedule)
        service_transfer = ServiceTransferProductFromTo(repository_schedule, graph)
        service_order = ServiceOrder(service_transfer)
        basket_1 = []
        storage_guid_4 = 4
        storage_pickup_guid_5 = 5
        service_transfer.add_storage_guid(storage_guid_4)
        service_transfer.add_storage_guid(storage_pickup_guid_5)
        transport_car_guid_2 = 2
        transport_jeep_guid_3 = 3
        transport_lada_guid_4 = 4
        service_transfer.add_transport_guid(transport_car_guid_2)
        #storage_depart_guid, datetime_depart, transport_guid, storage_arrival_guid, datetime_arrival
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 1, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 1, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 2, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 3, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 3, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 4, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 4, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 5, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 5, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 6, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 6, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 7, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 7, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 8, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 8, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 9, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 9, 16, 00, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 10, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 10, 16, 00, 00, tzinfo=pytz.UTC))

        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 2, 12, 30, 00, tzinfo=pytz.UTC), transport_jeep_guid_3, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 16, 10, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 5, 12, 30, 00, tzinfo=pytz.UTC), transport_jeep_guid_3, storage_pickup_guid_5, datetime.datetime(2019, 8, 5, 16, 10, 00, tzinfo=pytz.UTC))

        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 2, 11, 40, 00, tzinfo=pytz.UTC), transport_lada_guid_4, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 15, 10, 00, tzinfo=pytz.UTC))
        #service_transfer.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 6, 11, 40, 00, tzinfo=pytz.UTC), transport_lada_guid_4, storage_pickup_guid_5, datetime.datetime(2019, 8, 5, 15, 10, 00, tzinfo=pytz.UTC))

        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 1, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 1, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 2, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 3, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 3, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 4, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 4, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 5, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 5, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 6, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 6, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 7, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 7, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 8, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 8, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 9, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 9, 16, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 10, 14, 30, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_5, datetime.datetime(2019, 8, 10, 16, 00, 00, tzinfo=pytz.UTC))

        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 2, 12, 30, 00, tzinfo=pytz.UTC), transport_jeep_guid_3, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 16, 10, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 5, 12, 30, 00, tzinfo=pytz.UTC), transport_jeep_guid_3, storage_pickup_guid_5, datetime.datetime(2019, 8, 5, 16, 10, 00, tzinfo=pytz.UTC))

        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 2, 11, 40, 00, tzinfo=pytz.UTC), transport_lada_guid_4, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 15, 10, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_4, datetime.datetime(2019, 8, 6, 11, 40, 00, tzinfo=pytz.UTC), transport_lada_guid_4, storage_pickup_guid_5, datetime.datetime(2019, 8, 5, 15, 10, 00, tzinfo=pytz.UTC))


        datetime_create_order = datetime.datetime(2019, 8, 1, 15, 1, 23, tzinfo=pytz.UTC)
        datetime_pickup = datetime.datetime(2019, 8, 3, 14, 00, 00, tzinfo=pytz.UTC)

        self.assertEqual([storage_guid_4, storage_pickup_guid_5], service_transfer.all_storage_guids())
        self.assertEqual(
            [(storage_guid_4, storage_pickup_guid_5)],
            graph.chain_master(storage_guid_4, storage_pickup_guid_5)
        )
        self.assertEqual(
            [datetime.datetime(2019, 8, 2, 16, 00, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_car_guid_2, storage_guid_4, storage_pickup_guid_5, datetime.datetime(2019, 8, 2, 14, 30, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [datetime.datetime(2019, 8, 2, 14, 30, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(transport_car_guid_2, storage_guid_4, storage_pickup_guid_5, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                (
                    4,
                    datetime.datetime(2019, 8, 2, 14, 30, tzinfo=pytz.UTC),
                    2,
                    5,
                    datetime.datetime(2019, 8, 2, 16, 0, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_car_guid_2, storage_guid_4, storage_pickup_guid_5, datetime_create_order, datetime_pickup)
        )
        self.assertEqual([2,3,4,], repository_schedule.transport_guids_delivery_from_storage_to_storage(storage_guid_4, storage_pickup_guid_5))
        self.assertEqual(
            [
                (
                    4,
                    datetime.datetime(2019, 8, 2, 11, 40, tzinfo=pytz.UTC),
                    4,
                    5,
                    datetime.datetime(2019, 8, 2, 15, 10, tzinfo=pytz.UTC),
                ),
                (
                    4,
                    datetime.datetime(2019, 8, 2, 14, 30, tzinfo=pytz.UTC),
                    2,
                    5,
                    datetime.datetime(2019, 8, 2, 16, 0, tzinfo=pytz.UTC),
                ),
                (
                    4,
                    datetime.datetime(2019, 8, 2, 12, 30, tzinfo=pytz.UTC),
                    3,
                    5,
                    datetime.datetime(2019, 8, 2, 16, 10, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.edge_delivery(storage_guid_4, storage_pickup_guid_5, datetime_create_order, datetime_pickup)
        )
        transport_guids_allow_for_stock = [2]
        self.assertEqual(
            [
                (
                    4,
                    datetime.datetime(2019, 8, 2, 11, 40, tzinfo=pytz.UTC),
                    4,
                    5,
                    datetime.datetime(2019, 8, 2, 15, 10, tzinfo=pytz.UTC),
                ),
            ],
            service_transfer.fast_schedule(storage_guid_4, storage_pickup_guid_5, transport_guids_allow_for_stock, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [],
            service_order.create_order_sale_pickup(basket_1, storage_pickup_guid_5, datetime_create_order, datetime_pickup)
        )

    def test_create_order_sale_pickup_4(self):
        """
        Расширим пример test_create_order_sale_pickup_1 несуколькими вариантами доставки груза.

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

        Добаили в расписанеи скоростной поезд.

        Задача сразу после создания заказа, у нас в системе, содать план действий по его реализации.
        Пример плана по движению товара:
            2019, 7, 1, 19, 00, 00 отгрузка у поставщика с склада 1
            2019, 7, 1, 19, 00, 00 поезд скоростной 4 принял к перемещению заказ
            2019, 7, 2, 10, 23, 00 поезд 4 отгрузил закза
            2019, 7, 2, 10, 23, 00 склад 3 принял на зхарание заказ
            2019, 7, 7,  9, 13, 00 склад 3 отгрузил заказ клиенту 1
            2019, 7, 7,  9, 13, 00 клиенту 1 принял заказ
        План надо расширить движением денежных средств.
            ...


        """
        repository_schedule = RepositorySchedule()
        graph = Graph(repository_schedule)
        service_transfer = ServiceTransferProductFromTo(repository_schedule, graph)
        service_order = ServiceOrder(service_transfer)
        #service_order.create_order_sale_pickup(cargo, )
        basket_1 = []
        storage_donor_guid_1 = 1
        storage_guid_2 = 2
        storage_pickup_guid_3 = 3

        service_transfer.add_storage_guid(storage_donor_guid_1)
        service_transfer.add_storage_guid(storage_guid_2)
        service_transfer.add_storage_guid(storage_pickup_guid_3)

        transport_auto_guid_1 = 1
        transport_car_guid_2 = 2
        transport_auto_guid_3 = 3
        transport_train_guid_4 = 4

        service_transfer.add_transport_guid(transport_auto_guid_1)
        service_transfer.add_transport_guid(transport_car_guid_2)

        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 1, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 1, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 2, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 2, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 3, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 3, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 4, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 4, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 5, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 5, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 6, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 6, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 7, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 7, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 8, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 8, 19, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 9, 16, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_1, storage_guid_2, datetime.datetime(2019, 7, 9, 19, 00, 00, tzinfo=pytz.UTC))

        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 2, 15, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_3, storage_guid_2, datetime.datetime(2019, 7, 2, 19, 10, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 4, 15, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_3, storage_guid_2, datetime.datetime(2019, 7, 4, 19, 10, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 6, 15, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_3, storage_guid_2, datetime.datetime(2019, 7, 6, 19, 10, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 8, 15, 00, 00, tzinfo=pytz.UTC), transport_auto_guid_3, storage_guid_2, datetime.datetime(2019, 7, 8, 19, 10, 00, tzinfo=pytz.UTC))

        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 1, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 1, 11, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 2, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 2, 11, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 3, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 3, 11, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 4, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 4, 11, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 5, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 5, 11, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 6, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 6, 11, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 7, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 7, 11, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 8, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 8, 11, 00, 00, tzinfo=pytz.UTC))
        repository_schedule.add_schedule(storage_guid_2, datetime.datetime(2019, 7, 9, 10, 00, 00, tzinfo=pytz.UTC), transport_car_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 9, 11, 00, 00, tzinfo=pytz.UTC))

        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 1, 17, 00, 00, tzinfo=pytz.UTC), transport_train_guid_4, storage_pickup_guid_3, datetime.datetime(2019, 7, 3, 10, 45, 00, tzinfo=pytz.UTC))

        datetime_create_order = datetime.datetime(2019, 7, 1, 12, 15, 46, tzinfo=pytz.UTC)
        datetime_pickup = datetime.datetime(2019, 7, 7, 9, 13, 00, tzinfo=pytz.UTC)

        # start

        self.assertEqual([storage_donor_guid_1, storage_guid_2, storage_pickup_guid_3], service_transfer.all_storage_guids())
        self.assertEqual(
            [
                (storage_donor_guid_1, storage_pickup_guid_3),
                (storage_donor_guid_1, storage_guid_2, storage_pickup_guid_3),
            ],
            graph.chain_master(storage_donor_guid_1, storage_pickup_guid_3)
        )
        self.assertEqual(
            [datetime.datetime(2019, 7, 1, 19, 00, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_auto_guid_1, storage_donor_guid_1, storage_guid_2, datetime.datetime(2019, 7, 1, 16, 00, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_auto_guid_1, storage_donor_guid_1, storage_pickup_guid_3, datetime.datetime(2019, 7, 1, 16, 00, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [datetime.datetime(2019, 7, 2, 11, 00, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_car_guid_2, storage_guid_2, storage_pickup_guid_3, datetime.datetime(2019, 7, 2, 10, 00, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_car_guid_2, transport_auto_guid_1, storage_pickup_guid_3, datetime.datetime(2019, 7, 3, 10, 00, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [datetime.datetime(2019, 7, 3, 10, 45, 00, tzinfo=pytz.UTC)],
            repository_schedule.datetimes_arrival_for_delivery_by_transport_from_storage_to_storage_in_datetime_depart(
                transport_train_guid_4, storage_donor_guid_1, storage_pickup_guid_3, datetime.datetime(2019, 7, 1, 17, 00, 00, tzinfo=pytz.UTC)
            )
        )
        self.assertEqual(
            [
                datetime.datetime(2019, 7, 1, 16, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 2, 16, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 3, 16, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 4, 16, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 5, 16, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 6, 16, 00, 00, tzinfo=pytz.UTC),
            ],
            repository_schedule.datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(transport_auto_guid_1, storage_donor_guid_1, storage_guid_2, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                datetime.datetime(2019, 7, 2, 10, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 3, 10, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 4, 10, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 5, 10, 00, 00, tzinfo=pytz.UTC),
                datetime.datetime(2019, 7, 6, 10, 00, 00, tzinfo=pytz.UTC),
            ],
            repository_schedule.datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(transport_car_guid_2, storage_guid_2, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                datetime.datetime(2019, 7, 1, 17, 00, 00, tzinfo=pytz.UTC),
            ],
            repository_schedule.datetimes_depart_for_delivery_by_transport_from_storage_to_storage_in_datetime_range(transport_train_guid_4, storage_donor_guid_1, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                (1, datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 2, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 2, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 3, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 3, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 4, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 4, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 5, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 5, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 6, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 6, 19, 0, tzinfo=pytz.UTC),),
            ],
            service_transfer.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_auto_guid_1, storage_donor_guid_1, storage_guid_2, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                (1, datetime.datetime(2019, 7, 2, 15, 0, tzinfo=pytz.UTC), 3, 2, datetime.datetime(2019, 7, 2, 19, 10, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 4, 15, 0, tzinfo=pytz.UTC), 3, 2, datetime.datetime(2019, 7, 4, 19, 10, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 6, 15, 0, tzinfo=pytz.UTC), 3, 2, datetime.datetime(2019, 7, 6, 19, 10, tzinfo=pytz.UTC),),
            ],
            service_transfer.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_auto_guid_3, storage_donor_guid_1, storage_guid_2, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                (2, datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 3, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 3, 11, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 4, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 4, 11, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 5, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 5, 11, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 6, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 6, 11, 0, tzinfo=pytz.UTC),),
            ],
            service_transfer.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_car_guid_2, storage_guid_2, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [
                (1, datetime.datetime(2019, 7, 1, 17, 00, tzinfo=pytz.UTC), 4, 3, datetime.datetime(2019, 7, 3, 10, 45, tzinfo=pytz.UTC),),
            ],
            service_transfer.edge_transport_delivery_from_storage_to_storage_in_datetime_range(transport_train_guid_4, storage_donor_guid_1, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )

        self.assertEqual([1,3], repository_schedule.transport_guids_delivery_from_storage_to_storage(storage_donor_guid_1, storage_guid_2))
        self.assertEqual(
            [
                (1, datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 2, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 2, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 2, 15, 0, tzinfo=pytz.UTC), 3, 2, datetime.datetime(2019, 7, 2, 19, 10, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 3, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 3, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 4, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 4, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 4, 15, 0, tzinfo=pytz.UTC), 3, 2, datetime.datetime(2019, 7, 4, 19, 10, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 5, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 5, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 6, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 6, 19, 0, tzinfo=pytz.UTC),),
                (1, datetime.datetime(2019, 7, 6, 15, 0, tzinfo=pytz.UTC), 3, 2, datetime.datetime(2019, 7, 6, 19, 10, tzinfo=pytz.UTC),),
            ],
            service_transfer.edge_delivery(storage_donor_guid_1, storage_guid_2, datetime_create_order, datetime_pickup)
        )
        self.assertEqual([2,], repository_schedule.transport_guids_delivery_from_storage_to_storage(storage_guid_2, storage_pickup_guid_3))
        self.assertEqual(
            [
                (2, datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 3, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 3, 11, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 4, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 4, 11, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 5, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 5, 11, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 6, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 6, 11, 0, tzinfo=pytz.UTC),),
            ],
            service_transfer.edge_delivery(storage_guid_2, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )
        self.assertEqual([4,], repository_schedule.transport_guids_delivery_from_storage_to_storage(storage_donor_guid_1, storage_pickup_guid_3))
        self.assertEqual(
            [
                (1, datetime.datetime(2019, 7, 1, 17, 0, tzinfo=pytz.UTC), 4, 3, datetime.datetime(2019, 7, 3, 10, 45, tzinfo=pytz.UTC),),
            ],
            service_transfer.edge_delivery(storage_donor_guid_1, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )

        # Финал
        transport_guids_allow_for_stock = [1,2,3,4]
        self.assertEqual(
            [
                [
                    (1, datetime.datetime(2019, 7, 1, 17, 0, tzinfo=pytz.UTC), 4, 3, datetime.datetime(2019, 7, 3, 10, 45, tzinfo=pytz.UTC),),
                ],
                [
                    (1, datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC),),
                    (2, datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC),),
                ],
            ],
            service_transfer.fast_schedules_for_chains(storage_donor_guid_1, storage_pickup_guid_3, transport_guids_allow_for_stock, datetime_create_order, datetime_pickup)
        )
        transport_guids_allow_for_stock = [1,2,3,4]
        self.assertEqual(
            [
                (1, datetime.datetime(2019, 7, 1, 16, 0, tzinfo=pytz.UTC), 1, 2, datetime.datetime(2019, 7, 1, 19, 0, tzinfo=pytz.UTC),),
                (2, datetime.datetime(2019, 7, 2, 10, 0, tzinfo=pytz.UTC), 2, 3, datetime.datetime(2019, 7, 2, 11, 0, tzinfo=pytz.UTC),),
            ],
            service_transfer.fast_schedule(storage_donor_guid_1, storage_pickup_guid_3, transport_guids_allow_for_stock, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [],
            service_order.create_order_sale_pickup(basket_1, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )

        # Доабвили скоростной поед
        repository_schedule.add_schedule(storage_donor_guid_1, datetime.datetime(2019, 7, 1, 18, 00, 00, tzinfo=pytz.UTC), transport_train_guid_4, storage_pickup_guid_3, datetime.datetime(2019, 7, 2, 10, 23, 00, tzinfo=pytz.UTC))
        transport_guids_allow_for_stock = [1,2,3,4]
        self.assertEqual(
            [
                (1, datetime.datetime(2019, 7, 1, 18, 0, tzinfo=pytz.UTC), 4, 3, datetime.datetime(2019, 7, 2, 10, 23, tzinfo=pytz.UTC),),
            ],
            service_transfer.fast_schedule(storage_donor_guid_1, storage_pickup_guid_3, transport_guids_allow_for_stock, datetime_create_order, datetime_pickup)
        )
        self.assertEqual(
            [],
            service_order.create_order_sale_pickup(basket_1, storage_pickup_guid_3, datetime_create_order, datetime_pickup)
        )

