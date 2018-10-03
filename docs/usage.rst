=====
Usage
=====

To use dj_bitfields in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'dj_bitfields.apps.DjBitfieldsConfig',
        ...
    )

Add dj_bitfields's URL patterns:

.. code-block:: python

    from dj_bitfields import urls as dj_bitfields_urls


    urlpatterns = [
        ...
        url(r'^', include(dj_bitfields_urls)),
        ...
    ]
