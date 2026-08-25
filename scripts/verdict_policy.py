"""Politique minimale séparant jugement d'idée et autorisation d'action."""

VALID_VERDICTS = {"CONFIRMED", "NUANCED", "REJECTED", "PENDING"}


def evaluate_action(verdict: str, *, action_attached: bool, human_approved: bool = False) -> dict:
    if verdict not in VALID_VERDICTS:
        raise ValueError(f"verdict invalide: {verdict}")
    if not action_attached:
        return {
            "allowed": True,
            "mode": "IDEA_ONLY",
            "reason": f"{verdict} est consultatif; aucune action attachée",
        }
    if verdict == "PENDING":
        return {
            "allowed": False,
            "mode": "ACTION_BLOCKED",
            "reason": "PENDING interdit toute action",
        }
    if verdict == "NUANCED" and not human_approved:
        return {
            "allowed": False,
            "mode": "ACTION_BLOCKED",
            "reason": "NUANCED exige une approbation humaine pour agir",
        }
    if verdict == "REJECTED":
        return {
            "allowed": False,
            "mode": "ACTION_BLOCKED",
            "reason": "REJECTED interdit l'action proposée",
        }
    return {
        "allowed": True,
        "mode": "ACTION_CANDIDATE",
        "reason": "confiance suffisante; permissions et postconditions restent requises",
    }
