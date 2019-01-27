
from cloudshell.shell.core.driver_context import AutoLoadDetails, AutoLoadResource, AutoLoadAttribute
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext

from trafficgenerator.tgn_utils import ApiType
from testcenter.stc_app import init_stc


class StcHandler(object):

    def initialize(self, context, logger):
        """
        :type context: cloudshell.shell.core.driver_context.InitCommandContext
        """

        self.logger = logger

        controller = context.resource.attributes['STC Chassis Shell 2G.Controller Address']
        port = context.resource.attributes['STC Chassis Shell 2G.Controller TCP Port']
        port = int(port) if port else 80
        self.stc = init_stc(ApiType.rest, self.logger, rest_server=controller, rest_port=port)
        self.stc.connect()

    def get_inventory(self, context):
        """ Return device structure with all standard attributes

        :type context: cloudshell.shell.core.driver_context.AutoLoadCommandContext
        :rtype: cloudshell.shell.core.driver_context.AutoLoadDetails
        """

        self.resources = []
        self.attributes = []
        address = context.resource.address
        chassis = self.stc.hw.get_chassis(address)
        chassis.get_inventory()
        self._get_chassis(chassis)
        details = AutoLoadDetails(self.resources, self.attributes)
        return details

    def _get_chassis(self, chassis):
        """ Get chassis resource and attributes. """

        self._get_attributes('',
                             {'CS_TrafficGeneratorChassis.Model Name': chassis.attributes['Model'],
                              'STC Chassis Shell 2G.Serial Number': chassis.attributes['SerialNum'],
                              'STC Chassis Shell 2G.Server Description': '',
                              'CS_TrafficGeneratorChassis.Vendor': 'Spirent',
                              'CS_TrafficGeneratorChassis.Version': chassis.attributes['FirmwareVersion']})

        for module in chassis.modules.values():
            if module.attributes['Model']:
                self._get_module(module)

#         for power_supply in chassis.pss.values():
#             self._get_power_supply(power_supply)

    def _get_module(self, module):
        """ Get module resource and attributes. """

        relative_address = 'M' + module.attributes['Index']
        model = 'STC Chassis Shell 2G.GenericTrafficGeneratorModule'
        resource = AutoLoadResource(model=model,
                                    name='Module' + module.attributes['Index'],
                                    relative_address=relative_address)
        self.resources.append(resource)
        self._get_attributes(relative_address,
                             {'CS_TrafficGeneratorModule.Model Name': module.attributes['Model'],
                              model + '.Serial Number': module.attributes['SerialNum'],
                              model + '.Version': module.attributes['FirmwareVersion']})

        for port_group in module.pgs.values():
            self._get_port_group(relative_address, port_group)

    def _get_port_group(self, module_address, port_group):
        """ Get port group resource and attributes. """

        relative_address = module_address + '/PG' + port_group.attributes['Index']
        model = 'STC Chassis Shell 2G.GenericTrafficGeneratorPortGroup'
        resource = AutoLoadResource(model=model,
                                    name='PG' + port_group.attributes['Index'],
                                    relative_address=relative_address)
        self.resources.append(resource)
        for port in port_group.ports.values():
            self._get_port(relative_address, port)

    def _get_port(self, port_group_address, port):
        """ Get port resource and attributes. """

        relative_address = port_group_address + '/P' + port.attributes['Index']
        model = 'STC Chassis Shell 2G.GenericTrafficGeneratorPort'
        resource = AutoLoadResource(model=model,
                                    name='Port' + port.attributes['Index'],
                                    relative_address=relative_address)
        self.resources.append(resource)
        max_speed = self._get_max_speed(port.parent.parent.attributes['SupportedSpeeds'])
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='CS_TrafficGeneratorPort.Max Speed',
                                                 attribute_value=max_speed))
        configured_controllers = 'STC' if port.parent.attributes['TestPackage'] == 'stc' else 'Avalanche'
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='CS_TrafficGeneratorPort.Configured Controllers',
                                                 attribute_value=configured_controllers))

    def _get_power_supply(self, power_supply):
        """ get power supplies resource and attributes. """

        relative_address = 'PP' + power_supply.attributes['Index']
        resource = AutoLoadResource(model='Generic Power Port', name='PP' + power_supply.attributes['Index'],
                                    relative_address=relative_address)
        self.resources.append(resource)

    def _get_attributes(self, relative_address, attributes):
        """ Get attributes. """

        for attribute_name, attribute_value in attributes.items():
            self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                     attribute_name=attribute_name,
                                                     attribute_value=attribute_value))

    def set_port_attribute(self, context, port_name):
        """

        :param context:
        :param port_name: String example :'TestCenter Chassis 222/Module9/Port Group3/Port3':'TCP'
        :return:
        """
        splited_name = port_name.split(":")
        port_full_name = splited_name[0]
        port_logic_name = splited_name[1]

        my_api = CloudShellSessionContext(context).get_api()
        return my_api.SetAttributeValue(resourceFullPath=port_full_name, attributeName="Logical Name",
                                        attributeValue=port_logic_name)

    def _get_max_speed(self, supported_speeds):
        mb_speeds = list(float(s[:-1]) if s[-1] == 'M' else float(s[:-1])*1000 for s in supported_speeds)
        return str(int(max(mb_speeds))) if mb_speeds else '100'
