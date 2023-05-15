Introduction
==================


This repository contains a collection of Jinjamator tasks written by K-Businesscom and made publicly available.

Which tasks are included?
-------------------------

Currently following tasks have been made public:
    * `vendor/cisco/ise/hostname_to_devicegroup <https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks/tree/main/vendor/cisco/ise/hostname_to_devicegroup/>`_
    * `vendor/cisco/aci/maintenance/reports/contract_filters <https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks/tree/main/vendor/cisco/aci/maintenance/reports/contract_filters/>`_
    * `vendor/cisco/aci/maintenance/reports/contracts <https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks/tree/main/vendor/cisco/aci/maintenance/reports/contracts/>`_
    * `vendor/cisco/aci/maintenance/reports/endpoints <https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks/tree/main/vendor/cisco/aci/maintenance/reports/endpoints/>`_
    * `vendor/cisco/aci/maintenance/reports/epgs <https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks/tree/main/vendor/cisco/aci/maintenance/reports/epgs/>`_
    * `vendor/cisco/aci/maintenance/reports/interface_dom_stats <https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks/tree/main/vendor/cisco/aci/maintenance/reports/interface_dom_stats/>`_
    * `vendor/cisco/aci/maintenance/reports/interface_error_counter <https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks/tree/main/vendor/cisco/aci/maintenance/reports/interface_error_counter/>`_
    * `vendor/cisco/aci/configuration/add_legacy_vlan <https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks/tree/main/vendor/cisco/aci/configuration/add_legacy_vlan/>`_

Installation
==================


Install jinjamator by running:

.. code-block:: console

    pip3 install pipx
    python3 -m pipx ensurepath
    pipx install jinjamator
    pipx inject jinjamator git+https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks.git


Running Jinjamator as daemon
-----------------------------

To start jinjamator directly to fiddle around, run 

.. code-block:: console

    export JINJAMATOR_AAA_LOCAL_ADMIN_PASSWORD=_some_password
    export JINJAMATOR_AAA_LOCAL_ADMIN_USERNAME=admin
    jinjamator -t `pipx runpip jinjamator show jinjamator | grep Location| cut -d ' ' -f 2`/jinjamator/tasks/.internal/init_aaa`
    unset JINJAMATOR_AAA_LOCAL_ADMIN_PASSWORD
    unset JINJAMATOR_AAA_LOCAL_ADMIN_USERNAME
    jinjamator -d


Now you can navigate to http://localhost:5000 and login with your username and password.
Have fun.

License
-----------------

All files in this repository are licensed under the Apache License Version 2.0
