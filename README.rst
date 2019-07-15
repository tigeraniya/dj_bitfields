=============================
dj_bitfields
=============================

.. image:: https://badge.fury.io/py/dj_bitfields.svg
    :target: https://badge.fury.io/py/dj_bitfields

.. image:: https://travis-ci.org/tigeraniya/dj_bitfields.svg?branch=master
    :target: https://travis-ci.org/tigeraniya/dj_bitfields

.. image:: https://codecov.io/gh/tigeraniya/dj_bitfields/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/tigeraniya/dj_bitfields

Bit fields for pyscopg2/postgres db. Easily store grouped bit fields. Supports db operators for basic operations.

Documentation
-------------
simple usage:


::

    from dj_bitfields import BitStringField #import field

    schedule = BitStringField(max_length=8,default=None) #use in your models

as of now keep default=None.

and, or, xor and set operations are available on field in filters. 
Internally library uses [bitstring](https://pythonhosted.org/bitstring/) package. You will get Bits in python from db bit field.
Set operations are more useful. let us take an example of shop opening schedules. Each row corresponds to one shop. If we 
denote hour of day by one bit, than we need 24 bits to map full day schedule. Now to get shops opened within 9:30
to 11AM
::

    TestFieldModel.objects.get(schedule__intersects=Bits('0b000000001100000000000000'))

To get shops opened throughout 9:30 to 11AM.
::
    
    TestFieldModel.objects.get(schedule__superset=Bits('0b000000001100000000000000'))

To get shops opened only within 9:30 to 11AM.
::
    
    TestFieldModel.objects.get(schedule__subset=Bits('0b000000001100000000000000'))

To get shops not opened during 9:30 to 11AM.
::
    TestFieldModel.objects.get(schedule__disjoint=Bits('0b000000001100000000000000'))



Quickstart
----------

Install dj_bitfields::

    pip install dj_bitfields


Features
--------

* TODO


Credits
-------

Tools used in rendering this package:

*  BitField code is from https://github.com/zacharyvoase/django-postgres which looks abandoned now. 
lookup operators and set operations are new additions. Also this project is focus on single functionality.

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
