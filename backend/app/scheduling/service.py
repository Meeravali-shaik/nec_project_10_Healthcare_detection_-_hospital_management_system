from __future__ import annotations

from collections import Counter


class SchedulingService:
    def recommend_staffing(self, payload: dict) -> dict:
        patient_load = int(payload.get("patient_load", 0))
        bed_occupancy = float(payload.get("bed_occupancy", 0))
        emergency_cases = int(payload.get("emergency_cases", 0))
        department_demand = payload.get("department_demand", {}) or {}

        required_doctors = max(1, round(patient_load / 25 + emergency_cases / 5))
        required_nurses = max(2, round(patient_load / 10 + bed_occupancy / 20))
        shift_allocation = self._build_shift_allocation(required_doctors, required_nurses)
        recommendations = []
        if bed_occupancy > 90:
            recommendations.append("Increase ICU and ward coverage immediately.")
        if emergency_cases > 10:
            recommendations.append("Add emergency response staff and triage support.")
        if department_demand:
            busiest = max(department_demand.items(), key=lambda item: item[1])[0]
            recommendations.append(f"Prioritize staffing for {busiest} department.")
        return {
            "required_doctors": required_doctors,
            "required_nurses": required_nurses,
            "shift_allocation": shift_allocation,
            "staffing_recommendations": recommendations,
            "peak_hour_prediction": "18:00-22:00" if patient_load > 100 else "10:00-14:00",
        }

    def _build_shift_allocation(self, doctors: int, nurses: int) -> dict:
        return {
            "morning": {"doctors": max(1, doctors // 3), "nurses": max(1, nurses // 3)},
            "afternoon": {"doctors": max(1, doctors // 3), "nurses": max(1, nurses // 3)},
            "night": {"doctors": max(1, doctors - 2 * max(1, doctors // 3)), "nurses": max(1, nurses - 2 * max(1, nurses // 3))},
        }

