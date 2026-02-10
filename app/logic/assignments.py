import pandas as pd
from typing import Tuple, List


PRIORITY_ORDER = {
    "Urgent": 3,
    "High": 2,
    "Standard": 1
}


def normalize_list(val):
    if pd.isna(val):
        return set()
    return {v.strip().lower() for v in str(val).split(",")}


def match_missions(
    pilots: pd.DataFrame,
    drones: pd.DataFrame,
    missions: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    assignments = []
    conflicts = []

    pilots = pilots.copy()
    drones = drones.copy()
    missions = missions.copy()

    # Track consumption
    pilots["__assigned"] = False
    drones["__assigned"] = False

    # Priority-aware ordering
    missions["__priority_score"] = missions["priority"].map(PRIORITY_ORDER).fillna(0)
    missions = missions.sort_values(
        by=["__priority_score", "start_date"],
        ascending=[False, True]
    )

    for _, mission in missions.iterrows():
        mission_id = mission["project_id"]
        location = mission["location"].lower()
        req_skills = normalize_list(mission["required_skills"])
        req_certs = normalize_list(mission["required_certs"])

        eligible_pilots = []
        pilot_reasons = []

        for _, pilot in pilots.iterrows():
            if pilot["__assigned"]:
                pilot_reasons.append(
                    f"{pilot['pilot_id']}: already assigned to higher-priority mission"
                )
                continue

            reasons = []

            if pilot["location"].lower() != location:
                reasons.append("location mismatch")

            if not req_skills.issubset(normalize_list(pilot["skills"])):
                reasons.append("missing required skills")

            if not req_certs.issubset(normalize_list(pilot["certifications"])):
                reasons.append("missing required certifications")

            if pilot["status"].lower() != "available":
                reasons.append("not available")

            if reasons:
                pilot_reasons.append(f"{pilot['pilot_id']}: {', '.join(reasons)}")
            else:
                eligible_pilots.append(pilot)

        if not eligible_pilots:
            conflicts.append({
                "mission": mission_id,
                "type": "No eligible pilot",
                "reason": "; ".join(pilot_reasons)
            })
            continue

        eligible_drones = []
        drone_reasons = []

        for _, drone in drones.iterrows():
            if drone["__assigned"]:
                drone_reasons.append(
                    f"{drone['drone_id']}: already assigned to higher-priority mission"
                )
                continue

            reasons = []

            if drone["location"].lower() != location:
                reasons.append("location mismatch")

            if not req_skills.intersection(normalize_list(drone["capabilities"])):
                reasons.append("capability mismatch")

            if drone["status"].lower() != "available":
                reasons.append("not available")

            if reasons:
                drone_reasons.append(f"{drone['drone_id']}: {', '.join(reasons)}")
            else:
                eligible_drones.append(drone)

        if not eligible_drones:
            conflicts.append({
                "mission": mission_id,
                "type": "No eligible drone",
                "reason": "; ".join(drone_reasons)
            })
            continue

        # Assign first eligible (deterministic, explainable)
        chosen_pilot = eligible_pilots[0]
        chosen_drone = eligible_drones[0]

        pilots.loc[pilots["pilot_id"] == chosen_pilot["pilot_id"], "__assigned"] = True
        drones.loc[drones["drone_id"] == chosen_drone["drone_id"], "__assigned"] = True

        assignments.append({
            "mission": mission_id,
            "pilot_id": chosen_pilot["pilot_id"],
            "drone_id": chosen_drone["drone_id"],
            "priority": mission["priority"]
        })

    return (
        pd.DataFrame(assignments),
        pd.DataFrame(conflicts)
    )
