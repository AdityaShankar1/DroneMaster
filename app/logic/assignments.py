import pandas as pd
from datetime import datetime


def _parse_list(cell: str):
    if not cell or cell == "–":
        return set()
    return {x.strip().lower() for x in cell.split(",")}


def _parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def match_missions(pilots: pd.DataFrame,
                   drones: pd.DataFrame,
                   missions: pd.DataFrame):
    """
    Attempts to assign one pilot and one drone to each mission.
    Returns assignments and conflicts.
    """

    assignments = []
    conflicts = []

    # Normalize pilot fields
    pilots = pilots.copy()
    pilots["skills_set"] = pilots["skills"].apply(_parse_list)
    pilots["certs_set"] = pilots["certifications"].apply(_parse_list)
    pilots["available_from_date"] = pilots["available_from"].apply(_parse_date)

    # Normalize drone fields
    drones = drones.copy()
    drones["capabilities_set"] = drones["capabilities"].apply(_parse_list)

    for _, mission in missions.iterrows():
        mission_id = mission["project_id"]
        mission_location = mission["location"]
        req_skills = _parse_list(mission["required_skills"])
        req_certs = _parse_list(mission["required_certs"])
        start_date = _parse_date(mission["start_date"])

        # --- PILOT FILTERING ---
        eligible_pilots = pilots[
            (pilots["status"] == "Available") &
            (pilots["location"] == mission_location) &
            (pilots["available_from_date"] <= start_date)
        ]

        eligible_pilots = eligible_pilots[
            eligible_pilots["skills_set"].apply(lambda s: req_skills.issubset(s)) &
            eligible_pilots["certs_set"].apply(lambda s: req_certs.issubset(s))
        ]

        if eligible_pilots.empty:
            conflicts.append({
                "mission": mission_id,
                "type": "No eligible pilot",
            })
            continue

        pilot = eligible_pilots.iloc[0]

        # --- DRONE FILTERING ---
        eligible_drones = drones[
            (drones["status"] == "Available") &
            (drones["location"] == mission_location)
        ]

        # Accept any available drone in the same location
        # Capability matching can be refined later

        '''
        eligible_drones = eligible_drones[
                    eligible_drones["capabilities_set"].apply(
                        lambda c: bool(req_skills & c)
                    )
                ]'''

        if eligible_drones.empty:
            conflicts.append({
                "mission": mission_id,
                "type": "No eligible drone",
            })
            continue

        drone = eligible_drones.iloc[0]

        assignments.append({
            "mission": mission_id,
            "pilot_id": pilot["pilot_id"],
            "drone_id": drone["drone_id"]
        })

    return pd.DataFrame(assignments), pd.DataFrame(conflicts)
