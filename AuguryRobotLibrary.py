# AuguryRobotLibrary.py
import augury_api as api

class AuguryRobotLibrary:

    def init_simulation(self):
        api.init_simulation()

    def run_test_1(self, node_uuid: str, swu_file: str):
        api.run_test_1(node_uuid, swu_file)

    def run_test_2(self, serial: str, battery: int, backlog: int, last_version: int):
        api.run_test_2(serial, battery, backlog, last_version)
