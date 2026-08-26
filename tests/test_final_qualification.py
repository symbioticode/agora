from scripts.final_qualification import qualify


def test_current_evidence_satisfies_five_criteria():
    result = qualify()
    assert result["all_five_simultaneously_satisfied"]
    assert len(result["criteria"]) == 5
    assert all(item["passed"] for item in result["criteria"])
    assert result["qualification"] == "SUPERVISED_RESEARCH_INSTRUMENT"
