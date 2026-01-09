*** Settings ***
Library    ../AuguryRobotLibrary.py
Suite Setup    Init Simulation


*** Variables ***
# -------- Nodes + OTA artifacts --------
@{OTA_NODES}
...    AHN2_ABC11      ahn2_34.swu
...    CASSIA_ABC22    cassia_34.swu
...    MOXA_ABC33      moxa_34.swu


*** Test Cases ***
# =========================
# TEST1 – OTA (Nodes),Test3 The Node update if Node file match node type(AHN2_ABC11 nead fo mathe the file ahn2_xy.swu), uptate 33->34.
# =========================
TEST1 – OTA AHN2
    Run Test 1    AHN2_ABC11      ahn2_34.swu

TEST1 – OTA Cassia
    Run Test 1    CASSIA_ABC22    cassia_34.swu

TEST1 – OTA Moxa
    Run Test 1    MOXA_ABC33      moxa_34.swu


# =========================
# TEST2 – DFU (Endpoints)
# 2 EP × 2 states
# =========================


# ------------------ EP1 ---------------------Bat_level---BackLog----newVerNum
TEST2 – EP1 – Battery OK
    Run Test 2    AHN2_ABC11_EP1_SERIAL          4000       0          2

TEST2 – EP1 – Battery Low 
    Run Test 2    AHN2_ABC11_EP1_SERIAL          1000       0          3


# -------- Canary_A --------
TEST2 – Canary_A
    Run Test 2    AHN2_ABC11_Canary_A_SERIAL     4000       0          2

TEST2 – Canary_A – BackLog>0
    Run Test 2    AHN2_ABC11_Canary_A_SERIAL     4000       2          3

