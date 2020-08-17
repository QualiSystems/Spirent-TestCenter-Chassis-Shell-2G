
import logging

from cloudshell.shell.core.driver_context import AutoLoadDetails, InitCommandContext, AutoLoadCommandContext
from cloudshell.traffic.tg import TgChassisHandler

from trafficgenerator.tgn_utils import ApiType
from testcenter.stc_app import init_stc
from testcenter import StcPhyChassis, StcPhyModule, StcPhyPortGroup, StcPhyPort

from stc_data_model import (STC_Chassis_Shell_2G, GenericTrafficGeneratorModule, GenericTrafficGeneratorPortGroup,
                            GenericTrafficGeneratorPort, GenericPowerPort)


class StcHandler(TgChassisHandler):

    def initialize(self, context: InitCommandContext, logger: logging.Logger) -> None:
        resource = STC_Chassis_Shell_2G.create_from_context(context)
        super().initialize(resource, logger)

    def load_inventory(self, context: AutoLoadCommandContext) -> AutoLoadDetails:
        """ Return device structure with all standard attributes. """

        controller = self.resource.controller_address
        self.logger.debug(f'Controller - {controller}')
        port = self.resource.controller_tcp_port
        port = int(port) if port else 80
        self.logger.debug(f'Port - {port}')
        self.stc = init_stc(ApiType.rest, self.logger, rest_server=controller, rest_port=port)
        self.stc.connect()

        chassis = self.stc.hw.get_chassis(context.resource.address)
        chassis.get_inventory()
        self._load_chassis(chassis)
        return self.resource.create_autoload_details()

    def _load_chassis(self, chassis: StcPhyChassis) -> None:
        """ Get chassis resource and attributes. """

        self.resource.model_name = chassis.attributes['Model']
        self.resource.serial_number = chassis.attributes['SerialNum']
        self.resource.vendor = 'Spirent'
        self.resource.version = chassis.attributes['FirmwareVersion']

        for module in chassis.modules.values():
            if module.get_attributes('Model'):
                self._load_module(module)

#         for power_supply in chassis.pss.values():
#             self._load_power_supply(power_supply)

    def _load_module(self, module: StcPhyModule) -> None:
        """ Get module resource and attributes. """

        module_id = module.attributes['Index']
        gen_module = GenericTrafficGeneratorModule(f'Module{module_id}')
        self.resource.add_sub_resource(f'M{module_id}', gen_module)
        gen_module.model_name = module.attributes['Model']
        gen_module.serial_number = module.attributes['SerialNum']
        gen_module.version = module.attributes['FirmwareVersion']

        for port_group in module.pgs.values():
            self._load_port_group(gen_module, port_group)

    def _load_port_group(self, gen_module: GenericTrafficGeneratorModule, port_group: StcPhyPortGroup) -> None:
        """ Get port group resource and attributes. """

        pg_id = port_group.attributes['Index']
        gen_pg = GenericTrafficGeneratorPortGroup(f'PG{pg_id}')
        gen_module.add_sub_resource(f'PG{pg_id}', gen_pg)

        for port in port_group.ports.values():
            self._load_port(gen_pg, port)

    def _load_port(self, gen_pg: GenericTrafficGeneratorPortGroup, port: StcPhyPort) -> None:
        """ Get port resource and attributes. """

        port_id = port.attributes['Index']
        gen_port = GenericTrafficGeneratorPort(f'Port{port_id}')
        gen_pg.add_sub_resource(f'P{port_id}', gen_port)

        max_speed = self._get_max_speed(port.parent.parent.attributes['SupportedSpeeds'])
        gen_port.max_speed = max_speed
        configured_controllers = 'STC' if port.parent.attributes['TestPackage'] == 'stc' else 'Avalanche'
        gen_port.configured_controllers = configured_controllers

    def _load_power_supply(self, power_supply):
        """ get power supplies resource and attributes. """

        pp_id = power_supply.attributes['Index']
        gen_pp = GenericPowerPort(f'PP{pp_id}')
        self.resource.add_sub_resource(f'PP{pp_id}', gen_pp)

    def _get_max_speed(self, supported_speeds: str) -> str:
        mb_speeds = list(float(s[:-1]) if s[-1] == 'M' else float(s[:-1])*1000 for s in supported_speeds)
        return str(int(max(mb_speeds))) if mb_speeds else '100'
