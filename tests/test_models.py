#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_dj_bitfields
------------

Tests for `dj_bitfields` models module.
"""

from django.test import TestCase

from .models import TestFieldModel
from bitstring import Bits

class TestDj_bitfields(TestCase):

    def setUp(self):
        pass
        

    def test_and_operation(self):
        a = TestFieldModel(name="a",schedule=Bits('0b00110011'))
        a.save()
        b = TestFieldModel(name="b",schedule=Bits('0b00001100'))
        b.save()
        try:
            i = TestFieldModel.objects.get(schedule__and=Bits('0b00110011'))
            self.assertEqual(i.name,'a')
        except TestFieldModel.DoesNotExist as e:
            self.assertTrue(False,"No match found and operation")
        
        with self.assertRaises(TestFieldModel.DoesNotExist):
            g = TestFieldModel.objects.get(schedule__and=Bits('0b11000000'))

    def test_or_operation(self):
        a = TestFieldModel(name="a",schedule=Bits('0b00000000'))
        a.save()

        with self.assertRaises(TestFieldModel.DoesNotExist):
            TestFieldModel.objects.get(schedule__or=Bits('0b00000000'))

        b = TestFieldModel(name="b",schedule=Bits('0b00001000'))
        b.save()

        try:
            i = TestFieldModel.objects.get(schedule__or=Bits('0b00000000'))
            self.assertEqual(i.name,'b')
        except TestFieldModel.DoesNotExist as e:
            self.assertTrue(False,"No match found and operation")

    def test_intersection(self):
        TestFieldModel.objects.create(name="a",schedule=Bits('0b00001111'))
        TestFieldModel.objects.create(name="b",schedule=Bits('0b00110011'))

        with self.assertRaises(TestFieldModel.DoesNotExist):
            TestFieldModel.objects.get(schedule__intersects=Bits('0b11000000'))

        try:
            items  = sorted([i.name for i in TestFieldModel.objects.filter(schedule__or=Bits('0b00000011'))])
            self.assertEqual(items,['a','b'])
        except TestFieldModel.DoesNotExist as e:
            self.assertTrue(False,"No match found and operation")
    
    def test_superset(self):
        TestFieldModel.objects.create(name="a",schedule=Bits('0b00001111'))
        TestFieldModel.objects.create(name="b",schedule=Bits('0b00110011'))

        with self.assertRaises(TestFieldModel.DoesNotExist):
            TestFieldModel.objects.get(schedule__superset=Bits('0b11000000'))

        try:
            items  = sorted([i.name for i in TestFieldModel.objects.filter(schedule__superset=Bits('0b00000110'))])
            self.assertEqual(items,['a',])
        except TestFieldModel.DoesNotExist as e:
            self.assertTrue(False,"No match found and operation")
        
        try:
            items  = sorted([i.name for i in TestFieldModel.objects.filter(schedule__superset=Bits('0b00000011'))])
            self.assertEqual(items,['a','b'])
        except TestFieldModel.DoesNotExist as e:
            self.assertTrue(False,"No match found and operation")
    
    def test_subset(self):
        TestFieldModel.objects.create(name="a",schedule=Bits('0b00001111'))
        TestFieldModel.objects.create(name="b",schedule=Bits('0b00110011'))

        with self.assertRaises(TestFieldModel.DoesNotExist):
            TestFieldModel.objects.get(schedule__subset=Bits('0b00000011'))

        try:
            items  = sorted([i.name for i in TestFieldModel.objects.filter(schedule__subset=Bits('0b00011111'))])
            self.assertEqual(items,['a',])
        except TestFieldModel.DoesNotExist as e:
            self.assertTrue(False,"No match found and operation")

    
    def test_disjoint(self):
        TestFieldModel.objects.create(name="a",schedule=Bits('0b00001111'))
        TestFieldModel.objects.create(name="b",schedule=Bits('0b00110011'))

        with self.assertRaises(TestFieldModel.DoesNotExist):
            TestFieldModel.objects.get(schedule__disjoint=Bits('0b00000011'))

        try:
            items  = sorted([i.name for i in TestFieldModel.objects.filter(schedule__disjoint=Bits('0b11000000'))])
            self.assertEqual(items,['a','b'])
        except TestFieldModel.DoesNotExist as e:
            self.assertTrue(False,"No match found and operation")


    def tearDown(self):
        TestFieldModel.objects.all().delete()
