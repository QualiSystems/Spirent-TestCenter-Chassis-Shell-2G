#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `TestCenterChassisDriver`
"""

import sys
import logging

from shellfoundry.releasetools.test_helper import create_autoload_context_2g

from driver import TestCenterChassisDriver

address = '192.168.42.152'
controller = 'localhost'
port = '8888'


class TestStcChassisDriver(object):

    def setup(self):
        self.context = create_autoload_context_2g(model='STC Chassis Shell 2G', address=address, controller=controller,
                                                  port=port)
        self.driver = TestCenterChassisDriver()
        self.driver.initialize(self.context)
        self.driver.logger.addHandler(logging.StreamHandler(sys.stdout))

    def teardown(self):
        pass

    def test_hello_world(self):
        pass

    def test_auto_load(self):
        self.inventory = self.driver.get_inventory(self.context)
        for r in self.inventory.resources:
            print r.relative_address, r.model, r.name
        for a in self.inventory.attributes:
            print a.relative_address, a.attribute_name, a.attribute_value
