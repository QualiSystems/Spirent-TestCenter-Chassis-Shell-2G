#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `TestCenterChassisDriver`
"""

import sys
import logging
import unittest

from shellfoundry.releasetools.test_helper import create_autoload_context_2g

from driver import TestCenterChassisDriver

address = '192.168.42.218'
controller = '192.168.85.12'
port = '8888'
controller = '192.168.42.182'
port = ''


class TestStcChassisDriver(unittest.TestCase):

    def setUp(self):
        self.context = create_autoload_context_2g(model='STC Chassis Shell 2G', address=address, controller=controller,
                                                  port=port)
        self.driver = TestCenterChassisDriver()
        self.driver.initialize(self.context)
        self.driver.logger.addHandler(logging.StreamHandler(sys.stdout))

    def tearDown(self):
        pass

    def testHelloWorld(self):
        pass

    def testAutoload(self):
        self.inventory = self.driver.get_inventory(self.context)
        for r in self.inventory.resources:
            print r.relative_address, r.model, r.name
        for a in self.inventory.attributes:
            print a.relative_address, a.attribute_name, a.attribute_value


if __name__ == '__main__':
    sys.exit(unittest.main())
