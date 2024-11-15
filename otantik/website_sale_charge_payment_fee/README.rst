=============================
eCommerce: charge payment fee
=============================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:048ee9c9ac7ca6d8c7a29c05445bcee7211cb2e30db9d7c08a92b799f6082ebe
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fe--commerce-lightgray.png?logo=github
    :target: https://github.com/OCA/e-commerce/tree/12.0/website_sale_charge_payment_fee
    :alt: OCA/e-commerce
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/e-commerce-12-0/e-commerce-12-0-website_sale_charge_payment_fee
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/e-commerce&target_branch=12.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module allows to associate generic payment fee to online payment methods. Thus, when website user select a payment method with additional fee, an additional sale order line will be added to online order

**Table of contents**

.. contents::
   :local:

Configuration
=============

Click

Accounting -> Configuration -> Payments -> Payment Acquirers

open an acquirer and in CHARGE PAYMENT FEE tab, you can set the fee to be charged to customer.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/e-commerce/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/e-commerce/issues/new?body=module:%20website_sale_charge_payment_fee%0Aversion:%2012.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Agile Business Group
* AITIC S.A.S
* Quartile Limited

Contributors
~~~~~~~~~~~~

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* AITIC S.A. <info@aitic.com.ar>
* Quartile Limited <info@quartile.co>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/e-commerce <https://github.com/OCA/e-commerce/tree/12.0/website_sale_charge_payment_fee>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
