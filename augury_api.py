# Guy Malina

# Home Assignment – V&A Engineer
# augury_api.py


from augury_system import IoTSystem , BATTERY_THRESHOLD
import os

SYSTEM = IoTSystem()


def init_simulation():
    #start the simulation fill the nodes and endpoints whit data
    SYSTEM.init_simulation()
 
def api_get_node_by_uuid(uuid: str) -> dict:
    node = SYSTEM.get_node(uuid)
    node.try_ota_update()   
    return node.to_api_dict()

def api_post_version_to_ota_channel(ota_channel: str, version_artifact: str) -> int:
    return SYSTEM.post_to_ota_channel(ota_channel, version_artifact)

def api_get_endpoint_by_serial(serial_number: str) -> dict:
    ep = SYSTEM.get_endpoint(serial_number)

    # Try DFU on poll (similar to node OTA on poll)
    latest_version = SYSTEM.latest_ep_version.get(ep.hardware_type, ep.version)
    threshold = SYSTEM.get_battery_threshold(ep.hardware_type)

    if ep.backlog == 0 and ep.battery >= threshold:
        ep.try_dfu_update(latest_version)

    return ep.to_api_dict()

def api_set_endpoint_backlog(serial_number: str, backlog: int) -> None:
    SYSTEM.set_endpoint_backlog(serial_number, backlog)

def api_set_endpoint_battery(serial_number: str, battery: int) -> None:
    SYSTEM.set_endpoint_battery(serial_number, battery)

def get_battery_threshold(device_type: str) -> int:
    if device_type in BATTERY_THRESHOLD:
        return BATTERY_THRESHOLD[device_type]
    else:
        print (f"Device type {device_type} not supported")
        return None

def api_set_endpoint_version(serial_number: str, version: int) -> None:
    SYSTEM.set_endpoint_version(serial_number, version)

def api_check_endpoint_version(serial_number: str, expected_version: int) -> int:
    return SYSTEM.check_endpoint_version(serial_number, expected_version)



def run_test_1(node_uuid_for_test: str, swu_file_name: str):

    print("Simulation initialized")

    print("-" * 50)
    print("Test 1: OTA Update Happy Flow")
    print("-" * 50)

    # Test 1 ,3  : OTA Node Update Happy Flow
    #     - init and Verify initial version 33
    #     - update to version 34
    #     - confirm that the Node version is updated
    #     - confirm that the firmware file is match for node name

    # select node to update
    '''
    node list:
        AHN2_ABC11
        CASSIA_ABC22
        MOXA_ABC33
    '''

    node_uuid = node_uuid_for_test

    # 1. Verify initial version
    node = api_get_node_by_uuid(node_uuid)
    print("Initial version:", node["version"])

    # the artifact name need to match the node type
    swu_file = swu_file_name
    swu_version = int(swu_file.split('_')[1].split('.')[0])  # extract version from swu file name

    api_post_version_to_ota_channel(f"OTA_{node_uuid}", swu_file)
    node = api_get_node_by_uuid(node_uuid)

    if node["version"] == swu_version:
        print(f"OTA Happy Flow PASSED version is {node['version']}")
    else:
        print("OTA Happy Flow FAILED")
        raise AssertionError("OTA Happy Flow FAILED") # to fail the test (for robot framework)


def run_test_2(sn,bat_val,back_val,last_ver):
    # Test 2 : Endpoint DFU with Backlog + battery check
    # select Endpoint to update
    # check battery value is over TH by device type

    print("\nTest 2: Endpoint DFU with Backlog + Battery")

    '''
    EP serial list:

    AHN2_ABC11:
        AHN2_ABC11_EP1_SERIAL
        AHN2_ABC11_EP2_SERIAL
        AHN2_ABC11_Canary_A_SERIAL

    CASSIA_ABC22:
        CASSIA_ABC22_EP1_SERIAL
        CASSIA_ABC22_EP2_SERIAL
        CASSIA_ABC22_Canary_A_SERIAL

    MOXA_ABC33:
        MOXA_ABC33_EP1_SERIAL
        MOXA_ABC33_EP2_SERIAL
        MOXA_ABC33_Canary_A_SERIAL
    '''

    # EP For Test
    serial = sn 

    # Test Params
    battary_value = bat_val  # for the test set the battery value
    last_firmware_version = last_ver  # for the test set the last firmware version
    backlog_value = back_val  # for the test set the backlog value

    # api_set_endpoint_last_firmware_version(serial, last_firmware_version)

    api_set_endpoint_battery(serial, battary_value)  # set the battery value
    api_set_endpoint_backlog(serial, backlog_value)  # set the backlog value

    ep = api_get_endpoint_by_serial(serial)

    # get the device type from the ep dict
    device_type = ep["hardware_type"]

    # get the battery threshold for the device type
    threshold = get_battery_threshold(device_type)

    # check the current firmware version vs new firmware version
    #curren_firmware_version = ep["version"]
    if ep["version"] < last_firmware_version:
        need_update = True
    else:
        need_update = False

    # battery check for update over TH
    batt_ok = False
    if ep["battery"] > threshold:
        print(f"Battery over threshold {ep['battery']}, PASS\n")
        print("*" * 50)
        batt_ok = True
    else:
        print(f"Battery under threshold {ep['battery']}, FAIL\n")
        raise AssertionError("Battery under threshold") # to fail the test (for robot framework)
        print("*" * 50)
        batt_ok = False
    print("Battery test finished\n")

    # -------- Part B: backlog Check --------
    backlog_value = ep["backlog"]

    # check if backlog is greater than 0
    backlog_ok = False
    if backlog_value == 0:
        print("Backlog is 0, PASS")
        backlog_ok = True
    else:
        print("Backlog is greater than 0, FAIL")
        raise AssertionError("Backlog is greater than 0") # to fail the test (for robot framework)
        backlog_ok = False

    
    if need_update:
        if backlog_ok and batt_ok:
            print("Backlog and battery test passed")
            api_set_endpoint_version(serial, last_firmware_version)
            update_complete = True
        else:
            print("Backlog and battery test failed")
            raise AssertionError("Backlog and battery test failed") # to fail the test (for robot framework)
            update_complete = False
    else:
        print("No update needed version is up to date")
        raise AssertionError("No update needed version is up to date") # to fail the test (for robot framework)
        update_complete = False

#    if need_update and backlog_ok and batt_ok:
#        print("Backlog and battery test passed")
#        api_set_endpoint_version(serial, last_firmware_version)
#        update_complete = True
#    else:
#        print("Backlog and battery test failed")
#        raise AssertionError("Backlog and battery test failed") # to fail the test (for robot framework)
#        update_complete = False

    if update_complete:
        if api_check_endpoint_version(serial, last_firmware_version) == 200:
            print("Update complete")


if __name__ == "__main__":
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    init_simulation() 
    print("Simulation initialized")
    print("-"*50 + "\n")
    '''
    node list:
        AHN2_ABC11
        CASSIA_ABC22
        MOXA_ABC33
    '''
    node_uuid = "MOXA_ABC33"
    swu_file_name = "MOXA_34.swu"
    run_test_1(node_uuid, swu_file_name)

    '''
    EP serial list:

    AHN2_ABC11:
        AHN2_ABC11_EP1_SERIAL
        AHN2_ABC11_EP2_SERIAL
        AHN2_ABC11_Canary_A_SERIAL

    CASSIA_ABC22:
        CASSIA_ABC22_EP1_SERIAL
        CASSIA_ABC22_EP2_SERIAL
        CASSIA_ABC22_Canary_A_SERIAL

    MOXA_ABC33:
        MOXA_ABC33_EP1_SERIAL
        MOXA_ABC33_EP2_SERIAL
        MOXA_ABC33_Canary_A_SERIAL
    '''
    print("-"*50 + "\n")
    serial = "CASSIA_ABC22_Canary_A_SERIAL"
    bat_val = 5000
    back_val = 0
    last_ver = 2 # for the test set the last firmware version
    run_test_2(serial,bat_val,back_val,last_ver)














