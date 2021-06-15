from cloudshell.traffic.tg import TrafficDriver

from stc_handler import StcHandler


class TestCenterChassisDriver(TrafficDriver):
    def __init__(self):
        self.handler = StcHandler()

    def initialize(self, context):
        super().initialize(context)

    def cleanup(self):
        super().cleanup()

    def get_inventory(self, context):
        return super().get_inventory(context)
