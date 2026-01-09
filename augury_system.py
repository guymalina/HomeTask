# augury_system.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

BATTERY_THRESHOLD = {
    "EP1": 2500,
    "EP2": 2500,
    "Canary_A": 3600,
}

#split the node_uuid by the underscore and return the first part
def node_hw_type(node_uuid: str) -> str:
 #   "AHN2_NODE1" -> "AHN2"
    return node_uuid.split("_", 1)[0].upper()

def artifact_hw_type(artifact: str) -> str:
    # "moxa_34.swu" -> "MOXA"
    return artifact.split("_", 1)[0].upper()

def artifact_version(artifact: str) -> int:
    # "moxa_34.swu" -> 34
    base = artifact.rsplit(".", 1)[0]   # "moxa_34"
    return int(base.split("_", 1)[1])


@dataclass
class Endpoint:
    serial_number: str
    hardware_type: str          # EP1 / EP2 / Canary_A
    node_uuid: str              # requirement: uuid refers to Node_uuid
    version: int = 1
    battery: int = 5000
    backlog: int = 0
    #last_firmware_version: int = 1  

    def to_api_dict(self) -> dict:
        return {
            "serial_number": self.serial_number,
            "battery": self.battery,
            "hardware_type": self.hardware_type,
            "uuid": self.node_uuid,
            "version": self.version,
            "backlog": self.backlog,
            #"last_firmware_version": self.last_firmware_version,
            
        }

    def try_dfu_update(self, latest_version: int) -> None:
        if self.backlog > 0:
            return

        if latest_version > self.version:
            self.version = latest_version    

@dataclass
class Node:
    uuid: str
    version: int = 33 # init value
    ota_channel: str = ""
    endpoints: List[Endpoint] = field(default_factory=list) ## 3 end point same name but different serial number
    last_error: Optional[str] = None

    # Keep artifacts in the node (encapsulated), not as a global dict
    _ota_artifacts: List[str] = field(default_factory=list, repr=False)

    def post_ota_artifact(self, artifact: str) -> int:
        self._ota_artifacts.append(artifact)
        return 200

    def latest_ota_artifact(self) -> Optional[str]:
        if not self._ota_artifacts:
            return None
        return self._ota_artifacts[-1] 

    def to_api_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "ota_channel": self.ota_channel,
            "version": self.version,
            "Endpoints": [ep.to_api_dict() for ep in self.endpoints],
            "last_error": self.last_error,
        }

    def try_ota_update(self) -> None:
            """
            If there is an artifact in the OTA channel:
            - Update node version if artifact hardware matches node hardware.
            - Otherwise, do not update and set last_error.
            """
            latest = self.latest_ota_artifact() # get the latest artifact from the OTA channel
            if not latest: # if there is no artifact in the OTA channel
                return
            if node_hw_type(self.uuid) != artifact_hw_type(latest): # if the artifact hardware does not match the node hardware
                self.last_error = f"bad_firmware:{latest}"
                return
            self.version = artifact_version(latest) # update the node version
            self.last_error = None




class IoTSystem:

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.endpoints: Dict[str, Endpoint] = {}
                    # Latest available firmware version per endpoint type (for DFU tests)
        self.latest_ep_version: Dict[str, int] = {
            "EP1": 1,
            "EP2": 1,
            "Canary_A": 1
        }

    def init_simulation(self) -> None:
        self.nodes.clear()  # clear the nodes and endpoints start new simulation
        self.endpoints.clear()  # clear the nodes and endpoints start new simulation

        # define the nodes name and give unique name to each node for identification
        node_defs = [ 
            ("AHN2_ABC11", 33), 
            ("CASSIA_ABC22", 33),
            ("MOXA_ABC33", 33)
        ]
        
        # define the endpoints name 
        ep_defs =["EP1", "EP2", "Canary_A"] 

        for node_uuid, node_ver in node_defs:
            node = Node(uuid=node_uuid, version=node_ver, ota_channel=f"OTA_{node_uuid}")
            self.nodes[node_uuid] = node

            for ep_type in ep_defs:
                serial = f"{node_uuid}_{ep_type}_SERIAL"
                ep = Endpoint(serial_number=serial, hardware_type=ep_type, node_uuid=node_uuid)
                node.endpoints.append(ep)
                self.endpoints[serial] = ep


    def get_node(self, uuid: str) -> Node:
        if uuid not in self.nodes:
            raise KeyError(f"Node with uuid '{uuid}' was not found")
        return self.nodes[uuid] # return the node by the uuid from the nodes dict

    def get_endpoint(self, serial_number: str) -> Endpoint:
        if serial_number not in self.endpoints:
            raise KeyError(f"Endpoint with serial '{serial_number}' was not found")
        return self.endpoints[serial_number]

    # ---- OTA channel operations by channel name ----
    def post_to_ota_channel(self, ota_channel: str, artifact: str) -> int:
        node = self._find_node_by_channel(ota_channel)
        if not node:
            return 400
        return node.post_ota_artifact(artifact)

    def _find_node_by_channel(self, ota_channel: str) -> Optional[Node]:
        for node in self.nodes.values():
            if node.ota_channel == ota_channel:
                return node
        return None


        # --- DFU helpers ---
    def set_latest_ep_version(self, ep_type: str, version: int) -> None:
        if ep_type not in self.latest_ep_version:
            raise KeyError(f"Unknown endpoint type '{ep_type}'")
        self.latest_ep_version[ep_type] = int(version)

    def set_endpoint_backlog(self, serial_number: str, backlog: int) -> None:
        ep = self.get_endpoint(serial_number)
        ep.backlog = int(backlog)

    def set_endpoint_battery(self, serial_number: str, battery: int) -> None:
        ep = self.get_endpoint(serial_number)
        ep.battery = int(battery)

    def set_endpoint_version(self, serial_number: str, version: int) -> None:
        ep = self.get_endpoint(serial_number)
        ep.version = int(version)

    def check_endpoint_version(self, serial_number: str, expected_version: int) -> int:
        ep = self.get_endpoint(serial_number)
        if ep.version == int(expected_version):
            return 200
        else:
            return 400

    def get_battery_threshold(self, ep_type: str) -> int:
     return BATTERY_THRESHOLD[ep_type]
        










