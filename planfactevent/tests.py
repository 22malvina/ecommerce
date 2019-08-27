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

class TestEStorage(TestCase):
    def setUp(self):
        print("SETUP DATA FOR ...")
        self.assertEqual.__self__.maxDiff = None

    def test_seller(self):
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
