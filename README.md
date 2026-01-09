#Guy malina Home Assignment

# IoT DFU & OTA Robot Tests
## Overview
Robot Framework tests for validating a simulated IoT system.

- **Nodes:** AHN2, Cassia, Moxa  
- **Endpoints:** EP1, EP2, Canary_A  

Tests:
- **TEST1:** OTA updates on Nodes  
- **TEST2:** DFU validation on Endpoints (battery thresholds & failures)
---

INIT – Start Simulation
- Initialize the simulation environment
- Create all Nodes and Endpoints
- Generate Node UUIDs and Endpoint serial numbers

TEST1 – OTA (Nodes)
- Verify update file matches Node hardware type
- Update Node to version 34
- Verify Node version was updated

TEST2 – DFU (Endpoints)
- Check if update is required (new version available)
- Check battery threshold
- Check backlog
- Update Endpoint if all conditions are valid


## Project Structure

project_root/
├── test/iot_tests.robot
├── result/ (output.xml, report.html, log.html)
├── AuguryRobotLibrary.py
├── augury_system.py
├── augury_api.py
└── README.md


---

## Run Tests

Run all tests:
robot -d result tests/iot_tests.robot


Run test1:
robot -d result -t "TEST1*" tests/iot_tests.robot


Run test2:
robot -d result -t "TEST2*" tests/iot_tests.robot


---

## Notes
- Battery thresholds:
  - EP1 / EP2 → 2500
  - Canary_A → 3600

