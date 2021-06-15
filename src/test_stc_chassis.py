"""
Tests for TestCenterChassisDriver.
"""
import pytest
from _pytest.fixtures import SubRequest
from cloudshell.api.cloudshell_api import AttributeNameValue, CloudShellAPISession, ResourceInfo
from cloudshell.shell.core.driver_context import AutoLoadCommandContext
from cloudshell.traffic.tg import STC_CHASSIS_MODEL, TGN_CHASSIS_FAMILY
from shellfoundry_traffic.test_helpers import TestHelpers, create_session_from_config, print_inventory

from src.stc_driver import TestCenterChassisDriver


@pytest.fixture(params=[("192.168.65.24", "localhost", "8888")])
def dut(request: SubRequest) -> list:
    return request.param


@pytest.fixture(scope="session")
def session() -> CloudShellAPISession:
    yield create_session_from_config()


@pytest.fixture(scope="session")
def test_helpers(session: CloudShellAPISession) -> TestHelpers:
    """Yields initialized TestHelpers object."""
    yield TestHelpers(session)


@pytest.fixture()
def driver(test_helpers: TestHelpers, dut: list) -> TestCenterChassisDriver:
    address, controller_address, controller_port = dut
    attributes = {
        f"{STC_CHASSIS_MODEL}.Controller Address": controller_address,
        f"{STC_CHASSIS_MODEL}.Controller TCP Port": controller_port,
    }
    init_context = test_helpers.resource_init_command_context(TGN_CHASSIS_FAMILY, STC_CHASSIS_MODEL, address, attributes)
    driver = TestCenterChassisDriver()
    driver.initialize(init_context)
    yield driver


@pytest.fixture()
def autoload_context(test_helpers: TestHelpers, dut: list) -> AutoLoadCommandContext:
    address, controller_address, controller_port = dut
    attributes = {
        f"{STC_CHASSIS_MODEL}.Controller Address": controller_address,
        f"{STC_CHASSIS_MODEL}.Controller TCP Port": controller_port,
    }
    yield test_helpers.autoload_command_context(TGN_CHASSIS_FAMILY, STC_CHASSIS_MODEL, address, attributes)


@pytest.fixture()
def autoload_resource(session: CloudShellAPISession, test_helpers: TestHelpers, dut: list) -> ResourceInfo:
    address, controller_address, controller_port = dut
    attributes = [
        AttributeNameValue(f"{STC_CHASSIS_MODEL}.Controller Address", controller_address),
        AttributeNameValue(f"{STC_CHASSIS_MODEL}.Controller TCP Port", controller_port),
    ]
    resource = test_helpers.create_autoload_resource(STC_CHASSIS_MODEL, "test-stc", address, attributes)
    yield resource
    session.DeleteResource(resource.Name)


def test_autoload(driver: TestCenterChassisDriver, autoload_context: AutoLoadCommandContext) -> None:
    inventory = driver.get_inventory(autoload_context)
    print_inventory(inventory)


def test_autoload_session(session: CloudShellAPISession, autoload_resource: ResourceInfo, dut: dut) -> None:
    session.AutoLoad(autoload_resource.Name)
    resource_details = session.GetResourceDetails(autoload_resource.Name)
    assert len(resource_details.ChildResources) == 1
    assert resource_details.ChildResources[0].FullAddress == f"{dut[0]}/M1"
