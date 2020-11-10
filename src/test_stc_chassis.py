"""
Tests for `TestCenterChassisDriver`
"""

import pytest
from _pytest.fixtures import SubRequest

from cloudshell.api.cloudshell_api import CloudShellAPISession, AttributeNameValue
from cloudshell.shell.core.driver_context import AutoLoadCommandContext
from cloudshell.traffic.tg import STC_CHASSIS_MODEL
from shellfoundry.releasetools.test_helper import (create_session_from_deployment, create_init_command_context,
                                                   create_autoload_resource, create_autoload_context,
                                                   print_inventory)

from src.stc_driver import TestCenterChassisDriver


@pytest.fixture(params=[('192.168.65.28', 'localhost', '8888')])
def dut(request: SubRequest) -> list:
    return request.param


@pytest.fixture()
def session() -> CloudShellAPISession:
    yield create_session_from_deployment()


@pytest.fixture()
def autoload_context(session: CloudShellAPISession, dut: list) -> AutoLoadCommandContext:
    address, controller_address, controller_port = dut
    attributes = {f'{STC_CHASSIS_MODEL}.Controller Address': controller_address,
                  f'{STC_CHASSIS_MODEL}.Controller TCP Port': controller_port}
    yield create_autoload_context(session, 'CS_TrafficGeneratorChassis', STC_CHASSIS_MODEL, address, attributes)


@pytest.fixture()
def driver(session: CloudShellAPISession, dut: list) -> TestCenterChassisDriver:
    address, controller_address, controller_port = dut
    attributes = {f'{STC_CHASSIS_MODEL}.Controller Address': controller_address,
                  f'{STC_CHASSIS_MODEL}.Controller TCP Port': controller_port}
    init_context = create_init_command_context(session, 'CS_GenericResource', STC_CHASSIS_MODEL, address, attributes,
                                               'Resource')
    driver = TestCenterChassisDriver()
    driver.initialize(init_context)
    yield driver


@pytest.fixture()
def autoload_resource(session, dut):
    address, controller_address, controller_port = dut
    attributes = [
        AttributeNameValue(f'{STC_CHASSIS_MODEL}.Controller Address', controller_address),
        AttributeNameValue(f'{STC_CHASSIS_MODEL}.Controller TCP Port', controller_port)]
    resource = create_autoload_resource(session, 'CS_TrafficGeneratorChassis', STC_CHASSIS_MODEL, address, 'test-stc',
                                        attributes)
    yield resource
    session.DeleteResource(resource.Name)


def test_autoload(driver, autoload_context):
    inventory = driver.get_inventory(autoload_context)
    print_inventory(inventory)


def test_autoload_session(session, autoload_resource, dut):
    session.AutoLoad(autoload_resource.Name)
    resource_details = session.GetResourceDetails(autoload_resource.Name)
    assert len(resource_details.ChildResources) == 1
    assert resource_details.ChildResources[0].FullAddress == f'{dut[0]}/M1'
