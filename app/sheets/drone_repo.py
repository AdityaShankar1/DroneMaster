from app.sheets.client import read_sheet

DRONE_SHEET_ID = "128ugm11slKp_nEXZCE9mqM3zSPGwKyVliVTIgrRQhjs"
DRONE_RANGE = "drone_fleet!A1:G"

def get_drones():
    return read_sheet(DRONE_SHEET_ID, DRONE_RANGE)
