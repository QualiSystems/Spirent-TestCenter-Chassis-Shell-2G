"""
Tests for `TestCenterChassisDriver
"""

import pytest

from cloudshell.api.cloudshell_api import AttributeNameValue
from shellfoundry.releasetools.test_helper import create_autoload_resource_2g, create_session_from_deployment

stc_chassis = {'stc-stcweb': {'address': '192.168.42.157',
                              'controller': 'localhost',
                              'port': '8888',
                              'modules': 1},
               'stc-labserver': {'address': '192.168.42.218',
                                 'controller': '192.168.42.182',
                                 'port': '',
                                 'modules': 1}}


class TestStcChassisShell(object):

    session = None

    def setup(self):
        self.session = create_session_from_deployment()

    def teardown(self):
        self.session.DeleteResource(self.resource.Name)

    @pytest.mark.parametrize('chassis', ['stc-stcweb'])
    def test_stc_chassis(self, chassis):
        properties = stc_chassis[chassis]
        attributes = [AttributeNameValue('STC Chassis Shell 2G.Controller Address', properties['controller']),
                      AttributeNameValue('STC Chassis Shell 2G.Controller TCP Port', properties['port'])]
        self.resource = create_autoload_resource_2g(self.session, 'STC Chassis Shell 2G', properties['address'],
                                                    chassis, attributes)
        self.session.AutoLoad(self.resource.Name)
        resource_details = self.session.GetResourceDetails(self.resource.Name)
        assert(len(resource_details.ChildResources) == properties['modules'])
