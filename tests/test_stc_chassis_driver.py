#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `TestCenterChassisDriver`
"""

import sys
import logging

from shellfoundry.releasetools.test_helper import create_autoload_context_2g

from src.driver import TestCenterChassisDriver

address = '192.168.42.152'
controller = 'localhost'
port = '8888'


module_name = [
    '12 PORT 10/100/1000 Dual Media Rev B',
    'HYPERMETRICS CV 10G SFP+ 8-PORTS',
    'SPIRENT FX2 5-PORT 40/10GBE QSFP+'
    'HYPERMETRICS MX 10G SFP+ 8-PORTS',
    'HYPERMETRICS CM 10/100/1000 DUAL MEDIA 12-PORTS',
    'SPIRENT MX 2-PORT 100GBE CFP2',
    'SPIRENT FX2 20-PORT 10GBE QSFP+'
    ]


class TestStcChassisDriver(object):

    def setup(self):
        self.context = create_autoload_context_2g(model='STC Chassis Shell 2G', address=address, controller=controller,
                                                  port=port)
        self.context.resource.attributes['STC Chassis Shell 2G.Split Dual Media'] = True
        self.driver = TestCenterChassisDriver()
        self.driver.initialize(self.context)
        self.driver.logger.addHandler(logging.StreamHandler(sys.stdout))

    def teardown(self):
        pass

    def test_hello_world(self):
        pass

    def test_auto_load(self):
        inventory = self.driver.get_inventory(self.context)
        print('\n')
        for r in inventory.resources:
            print('{}, {}, {}'.format(r.relative_address, r.model, r.name))
        print('\n')
        for a in inventory.attributes:
            print('{}, {}, {}'.format(a.relative_address, a.attribute_name, a.attribute_value))
