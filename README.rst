==========
awspricing
==========

A Python library for working with the `AWS (China) Price List API <http:://docs.amazonaws.cn/en_us/aws/latest/userguide/billing-and-payment.html>`_.

Features:

* Simple boto3-like interface
* Service-specific helpers (only EC2 and RDS thus far)
* Local caching support

This library is modified based on https://github.com/lyft/awspricing.


Installation:
------------

.. code-block:: sh

    $ python setup.py biuld
    $ python setup.py install


Usage
-----

.. code-block:: python

    import awscnpricing
    ec2_offer = awscnpricing.offer('AmazonEC2')


    ec2_offer.search_skus(
      instance_type='c4.large',
      location='China (Beijing)',
      operating_system='Linux',
      )

    ec2_offer.reserved_hourly(
      'r5.24xlarge',
      operating_system='Linux',
      lease_contract_length='1yr',
      offering_class='standard',
      purchase_option='All Upfront',
      region='cn-north-1'
      )
    e2_offer.reserved_upfront(
      'r5.24xlarge',
      operating_system='Linux',
      lease_contract_length='1yr',
      offering_class='standard',
      purchase_option='All Upfront',
      region='cn-north-1'
      )
..
