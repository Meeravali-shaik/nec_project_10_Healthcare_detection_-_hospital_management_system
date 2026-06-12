from __future__ import annotations


class OptimizationService:
    def recommend(self, payload: dict) -> list[dict]:
        recommendations = []
        icu_occupancy = float(payload.get("icu_occupancy", 0))
        oxygen_usage = float(payload.get("oxygen_usage", 0))
        emergency_cases = int(payload.get("emergency_cases", 0))
        if icu_occupancy >= 95:
            recommendations.append({
                "recommendation_type": "Bed Allocation",
                "title": "Allocate additional ICU beds",
                "message": "Allocate 3 additional ICU beds immediately.",
                "priority": "Critical",
                "metadata_json": {"icu_occupancy": icu_occupancy},
            })
        if oxygen_usage >= 90:
            recommendations.append({
                "recommendation_type": "Inventory Replenishment",
                "title": "Replenish Oxygen Inventory",
                "message": "Restock oxygen cylinders and concentrators.",
                "priority": "High",
                "metadata_json": {"oxygen_usage": oxygen_usage},
            })
        if emergency_cases >= 5:
            recommendations.append({
                "recommendation_type": "Staffing",
                "title": "Add emergency doctors",
                "message": "Add 2 Emergency Doctors for peak coverage.",
                "priority": "High",
                "metadata_json": {"emergency_cases": emergency_cases},
            })
        if not recommendations:
            recommendations.append({
                "recommendation_type": "Monitoring",
                "title": "Maintain current allocation",
                "message": "Operational metrics are within safe thresholds.",
                "priority": "Low",
                "metadata_json": {},
            })
        return recommendations

