import os
from unittest import TestCase, main

from datetime import datetime, date
from time import time

from defcollect.datatypes import *

from helpers import setup_default_env

class TestDataTypes(TestCase):
    """Check we can enumerate basic data types."""

    def setUp(self):
        setup_default_env()

    def test_available_datatypes(self):
        """Data types can be listed."""
        types_list = DataType.list_types()
        self.assertIsNotNone(types_list)
        self.assertEqual(len(types_list), 4)

    def test_create_numbertype(self):
        """Can create a number data type."""
        number_tclass = DataType.type_class('number')
        self.assertIsNotNone(number_tclass)
        num_field = number_tclass('price', {'nullable': True})
        with self.assertRaises(ValueError):
            num_field.validate('foo')
        res = num_field.validate('3')
        self.assertEqual(res, 3)

    def test_create_enumtype(self):
        """Can create an enum data type."""
        enum_tclass = DataType.type_class('enum')
        self.assertIsNotNone(enum_tclass)
        with self.assertRaises(ValueError):
            # enum requires 'options' as valid values
            enum_field = enum_tclass('color', {'nullable': False })
        enum_field = enum_tclass('color', {'nullable': False,
                                          'options': ['red', 'green', 'blue']})
        with self.assertRaises(ValueError):
            enum_field.validate('purple')
        res = enum_field.validate('red')
        self.assertEqual(res, 'red')

    def test_create_datettype(self):
        """Can create a date data type."""
        date_tclass = DataType.type_class('date')
        self.assertIsNotNone(date_tclass)
        date_field = date_tclass('default_date')
        with self.assertRaises(ValueError):
            date_field.validate('foo-bar')
        valid_date = date_field.validate('2018-02-23')
        self.assertTrue(isinstance(valid_date, date))
        valid_date = date_field.validate(datetime.now())
        self.assertTrue(isinstance(valid_date, date))
        valid_date = date_field.validate(date.today())
        with self.assertRaises(ValueError):
            date_field.validate(time())
        ts_date_field = date_tclass('timestamp_date', {'format': 'timestamp'})
        valid_date = ts_date_field.validate(time())
        self.assertTrue(isinstance(valid_date, date))
        with self.assertRaises(ValueError):
            non_valid_none = ts_date_field.validate(None)

    def test_create_texttype(self):
        """Can create text data type."""
        text_tclass = DataType.type_class('text')
        self.assertIsNotNone(text_tclass)
        text_field = text_tclass('name')
        with self.assertRaises(ValueError):
            text_field.validate(None)
        valid_value = text_field.validate('foo')
        self.assertEqual(valid_value, 'foo')
        valid_value = text_field.validate(3)
        self.assertEqual(valid_value, '3')
        nullable_field = text_tclass('street', {'nullable': True})
        none_value = nullable_field.validate(None)
        self.assertIsNone(none_value)


if __name__ == '__main__':
    main()
