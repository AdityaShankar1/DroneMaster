from datetime import datetime
import pandas as pd

from app.sheets.pilot_repo import get_pilots
from app.sheets.drone_repo import get_drones
from app.sheets.mission_repo import get_missions


def parse_date(d):
    return datetime.strptime(d, "%Y-%m-%d")


def date_overlap(start1, end1, start2, end2):
    return not (end1 < start2 or end2 < start1)


def match_missions(pilots: pd.DataFrame,
                   drones: pd.DataFrame,
                   missions: pd.DataFrame):
    assignments = []
    conflicts = []

    pilot_assignments = {}   # pilot_id -> (start, end)
    drone_assignments = {}   # drone_id -> (start, end)

    for _, mission in missions.iterrows():
        mission_id = mission["project_id"]
        mission_loc = mission["location"]
        mission_start = parse_date(mission["start_date"])
        mission_end = parse_date(mission["end_date"])

        required_skills = {
            s.strip().lower()
            for s in mission["required_skills"].split(",")
        }
        required_certs = {
            c.strip().lower()
            for c in mission["required_certs"].split(",")
        }

        eligible_pilots = []
        pilot_rejection_reasons = []

        for _, pilot in pilots.iterrows():
            reasons = []

            if pilot["location"] != mission_loc:
                reasons.append("location mismatch")

            pilot_skills = {
                s.strip().lower()
                for s in pilot["skills"].split(",")
            }
            if not required_skills.issubset(pilot_skills):
                reasons.append("missing required skills")

            pilot_certs = {
                c.strip().lower()
                for c in pilot["certifications"].split(",")
            }
            if not required_certs.issubset(pilot_certs):
                reasons.append("missing required certifications")

            available_from = parse_date(pilot["available_from"])
            if available_from > mission_start:
                reasons.append("not available on start date")

            pid = pilot["pilot_id"]
            if pid in pilot_assignments:
                assigned_start, assigned_end = pilot_assignments[pid]
                if date_overlap(
                    mission_start, mission_end,
                    assigned_start, assigned_end
                ):
                    reasons.append("pilot already assigned during mission window")

            if reasons:
                pilot_rejection_reasons.append(
                    f"{pid}: {', '.join(reasons)}"
                )
            else:
                eligible_pilots.append(pilot)

        if not eligible_pilots:
            conflicts.append({
                "mission": mission_id,
                "type": "No eligible pilot",
                "reason": "; ".join(pilot_rejection_reasons)
            })
            continue

        pilot = eligible_pilots[0]
        pid = pilot["pilot_id"]

        eligible_drones = []
        drone_rejection_reasons = []

        for _, drone in drones.iterrows():
            reasons = []

            if drone["location"] != mission_loc:
                reasons.append("location mismatch")

            if drone["status"].lower() != "available":
                reasons.append("drone not available")

            drone_caps = {
                c.strip().lower()
                for c in drone["capabilities"].split(",")
            }
            if not required_skills.issubset(drone_caps):
                reasons.append("capability mismatch")

            did = drone["drone_id"]
            if did in drone_assignments:
                assigned_start, assigned_end = drone_assignments[did]
                if date_overlap(
                    mission_start, mission_end,
                    assigned_start, assigned_end
                ):
                    reasons.append("drone already assigned during mission window")

            if reasons:
                drone_rejection_reasons.append(
                    f"{did}: {', '.join(reasons)}"
                )
            else:
                eligible_drones.append(drone)

        if not eligible_drones:
            conflicts.append({
                "mission": mission_id,
                "type": "No eligible drone",
                "reason": "; ".join(drone_rejection_reasons)
            })
            continue

        drone = eligible_drones[0]
        did = drone["drone_id"]

        assignments.append({
            "mission": mission_id,
            "pilot_id": pid,
            "drone_id": did
        })

        pilot_assignments[pid] = (mission_start, mission_end)
        drone_assignments[did] = (mission_start, mission_end)

    return pd.DataFrame(assignments), pd.DataFrame(conflicts)


if __name__ == "__main__":
    pilots = get_pilots()
    drones = get_drones()
    missions = get_missions()

    assignments, conflicts = match_missions(pilots, drones, missions)

    print("Assignments:")
    print(assignments)

    print("\nConflicts:")
    print(conflicts)
