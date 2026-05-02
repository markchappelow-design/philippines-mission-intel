from typing import List
from sources.source_models import SourcePayload


def evaluate_posture(payloads: List[SourcePayload]) -> dict:
    amber_flags = 0
    red_flags = 0
    triggers: list[str] = []

    for p in payloads:
        name = p.section_name.lower()
        content = p.content.lower()

        if "embassy" in name and "demonstration" in content:
            amber_flags += 1
            triggers.append("Embassy demonstration alert present")

        if "weather" in name and any(term in content for term in ["storm", "thunderstorm", "violent showers", "heavy rain"]):
            amber_flags += 1
            triggers.append("Weather degradation affecting movement assumptions")

        if "naia" in name and any(term in content for term in ["unreliable", "dead article", "supplemental context only"]):
            amber_flags += 1
            triggers.append("NAIA public reporting reliability degraded")

        if "priority intelligence" in name and "pla" in content:
            amber_flags += 1
            triggers.append("Regional military signaling remains elevated")

        if "terrorism" in name and any(term in content for term in ["active terrorist", "attack", "imminent", "credible threat"]):
            red_flags += 1
            triggers.append("Active terrorism indicator detected")

        if "strategic situation" in name and any(term in content for term in ["direct crisis", "airline routing", "regional security deterioration"]):
            amber_flags += 1
            triggers.append("Regional escalation risk affecting travel planning")

    def build_decision_guidance(posture: str, triggers: list[str]) -> str:
        lines = [
            f"Posture: {posture}",
            "",
            "Triggering factors:",
        ]

        if triggers:
            lines.extend([f"- {t}" for t in triggers])
        else:
            lines.append("- No significant movement triggers detected")

        lines.append("")

        if posture == "GREEN":
            lines.extend([
                "Action:",
                "- Proceed with planned movement.",
                "- Maintain routine monitoring only.",
                "- No contingency execution required at this time.",
            ])
        elif posture == "AMBER":
            lines.extend([
                "Action:",
                "- Proceed with caution.",
                "- Reconfirm flights and departure flexibility.",
                "- Review strict contingency diversion options within 12 hours.",
                "- Monitor Embassy, weather, and airport updates closely.",
            ])
        else:
            lines.extend([
                "Action:",
                "- Delay movement or prepare immediate contingency execution.",
                "- Prioritize departure feasibility and alternate routing now.",
                "- Revalidate airport access, onward movement, and fallback destination assumptions.",
            ])

        return "\n".join(lines)
    
        decision = evaluate_posture(payloads)
        posture = decision["posture"]
        triggers = decision["triggers"]

        section_map["Decision Guidance"] = build_decision_guidance(posture, triggers)