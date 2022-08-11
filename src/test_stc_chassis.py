"""
Tests for TestCenterChassisDriver.
"""
# pylint: disable=redefined-outer-name
from typing import Iterable

import pytest
from _pytest.fixtures import SubRequest
from cloudshell.api.cloudshell_api import AttributeNameValue, CloudShellAPISession, ResourceInfo
from cloudshell.shell.core.driver_context import AutoLoadCommandContext
from cloudshell.traffic.tg import STC_CHASSIS_MODEL, TGN_CHASSIS_FAMILY
from shellfoundry_traffic.test_helpers import TestHelpers, create_session_from_config, print_inventory

from stc_driver import TestCenterChassisDriver


@pytest.fixture(params=[("192.168.65.31", "localhost", "9090")])
def dut(request: SubRequest) -> list:
    """Yield STC device under test parameters."""
    return request.param


@pytest.fixture(scope="session")
def session() -> CloudShellAPISession:
    """Yield session."""
    return create_session_from_config()


@pytest.fixture(scope="session")
def test_helpers(session: CloudShellAPISession) -> TestHelpers:
    """Yield initialized TestHelpers object."""
    return TestHelpers(session)


@pytest.fixture()
def driver(test_helpers: TestHelpers, dut: list) -> Iterable[TestCenterChassisDriver]:
    """Yield initialized TestCenterChassisDriver."""
    address, controller_address, controller_port = dut
    attributes = {
        f"{STC_CHASSIS_MODEL}.Controller Address": controller_address,
        f"{STC_CHASSIS_MODEL}.Controller TCP Port": controller_port,
    }
    init_context = test_helpers.resource_init_command_context(TGN_CHASSIS_FAMILY, STC_CHASSIS_MODEL, address, attributes)
    driver = TestCenterChassisDriver()
    driver.initialize(init_context)
    yield driver
    driver.cleanup()


@pytest.fixture()
def autoload_context(test_helpers: TestHelpers, dut: list) -> AutoLoadCommandContext:
    """Yield STC chassis resource for shell autoload testing."""
    address, controller_address, controller_port = dut
    attributes = {
        f"{STC_CHASSIS_MODEL}.Controller Address": controller_address,
        f"{STC_CHASSIS_MODEL}.Controller TCP Port": controller_port,
    }
    return test_helpers.autoload_command_context(TGN_CHASSIS_FAMILY, STC_CHASSIS_MODEL, address, attributes)


@pytest.fixture()
def autoload_resource(session: CloudShellAPISession, test_helpers: TestHelpers, dut: list) -> Iterable[ResourceInfo]:
    """Yield STC resource for shell autoload testing."""
    address, controller_address, controller_port = dut
    attributes = [
        AttributeNameValue(f"{STC_CHASSIS_MODEL}.Controller Address", controller_address),
        AttributeNameValue(f"{STC_CHASSIS_MODEL}.Controller TCP Port", controller_port),
    ]
    resource = test_helpers.create_autoload_resource(STC_CHASSIS_MODEL, "tests/test-stc", address, attributes)
    yield resource
    session.DeleteResource(resource.Name)


def test_autoload(driver: TestCenterChassisDriver, autoload_context: AutoLoadCommandContext) -> None:
    """Test direct (driver) auto load command."""
    inventory = driver.get_inventory(autoload_context)
    print_inventory(inventory)


def test_autoload_session(session: CloudShellAPISession, autoload_resource: ResourceInfo, dut: list) -> None:
    """Test indirect (shell) auto load command."""
    session.AutoLoad(autoload_resource.Name)
    resource_details = session.GetResourceDetails(autoload_resource.Name)
    assert len(resource_details.ChildResources) == 1
    assert resource_details.ChildResources[0].FullAddress == f"{dut[0]}/M1"
