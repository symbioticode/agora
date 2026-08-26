from scripts.final_qualification import qualify


def test_current_evidence_satisfies_five_criteria():
    result = qualify()
    assert result["all_five_simultaneously_satisfied"]
    assert len(result["criteria"]) == 5
    assert all(item["passed"] for item in result["criteria"])
    assert result["qualification"] == "SUPERVISED_RESEARCH_INSTRUMENT"
    correction = result["evidence_corrections"][0]
    assert correction["status"] == "REPLACEMENT_COMPLETED"
    assert correction["scores_reproduced"] and correction["winner_reproduced"]
    assert correction["recorded_cost_usd"]["combined"] == 0.137604
    assert correction["unmeasured_events"]
