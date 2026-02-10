import pandas as pd

PRIORITY_BONUS = {
    "Urgent": 50,
    "High": 30,
    "Standard": 0
}

PENALTIES = {
    "location_mismatch": -20,
    "missing_skill": -30,
    "missing_cert": -40,
    "capability_mismatch": -30
}


def _split(val):
    if pd.isna(val) or val == "–":
        return []
    return [v.strip() for v in str(val).split(",")]


def score_pilot(pilot, mission):
    score = 0
    reasons = []

    if pilot["location"] != mission["location"]:
        score += PENALTIES["location_mismatch"]
        reasons.append("pilot location mismatch")

    pilot_skills = _split(pilot["skills"])
    required_skills = _split(mission["required_skills"])
    if not set(required_skills).issubset(set(pilot_skills)):
        score += PENALTIES["missing_skill"]
        reasons.append("missing required skill")

    pilot_certs = _split(pilot["certifications"])
    required_certs = _split(mission["required_certs"])
    if not set(required_certs).issubset(set(pilot_certs)):
        score += PENALTIES["missing_cert"]
        reasons.append("missing required certification")

    return score, reasons


def score_drone(drone, mission):
    score = 0
    reasons = []

    if drone["status"] == "Maintenance":
        return None, ["drone under maintenance"]

    drone_caps = _split(drone["capabilities"])
    required_skills = _split(mission["required_skills"])
    if not set(required_skills).issubset(set(drone_caps)):
        score += PENALTIES["capability_mismatch"]
        reasons.append("drone capability mismatch")

    if drone["location"] != mission["location"]:
        score += PENALTIES["location_mismatch"]
        reasons.append("drone location mismatch")

    return score, reasons


def match_missions(pilots, drones, missions):
    assignments = []
    conflicts = []

    missions = missions.copy()
    missions["priority_rank"] = missions["priority"].map(
        {"Urgent": 0, "High": 1, "Standard": 2}
    )
    missions = missions.sort_values("priority_rank")

    used_pilots = set()
    used_drones = set()

    for _, mission in missions.iterrows():
        best = None
        best_score = float("-inf")
        best_reasons = []

        for _, pilot in pilots.iterrows():
            if pilot["pilot_id"] in used_pilots:
                continue
            if pilot["status"] != "Available":
                continue

            pilot_score, pilot_reasons = score_pilot(pilot, mission)

            for _, drone in drones.iterrows():
                if drone["drone_id"] in used_drones:
                    continue

                drone_score, drone_reasons = score_drone(drone, mission)
                if drone_score is None:
                    continue  # hard fail

                total_score = (
                    pilot_score
                    + drone_score
                    + PRIORITY_BONUS.get(mission["priority"], 0)
                )

                if total_score > best_score:
                    best_score = total_score
                    best = (pilot, drone)
                    best_reasons = pilot_reasons + drone_reasons

        if best and best_score >= 0:
            pilot, drone = best
            used_pilots.add(pilot["pilot_id"])
            used_drones.add(drone["drone_id"])

            assignments.append({
                "mission": mission["project_id"],
                "pilot_id": pilot["pilot_id"],
                "drone_id": drone["drone_id"],
                "score": best_score,
                "violations": "; ".join(best_reasons) if best_reasons else "None"
            })
        else:
            conflicts.append({
                "mission": mission["project_id"],
                "type": "No viable assignment",
                "reason": "All options scored below threshold"
            })

    return pd.DataFrame(assignments), pd.DataFrame(conflicts)
