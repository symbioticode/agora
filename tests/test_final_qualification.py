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
    costs = correction["recorded_cost_usd"]
    assert costs["valid_anthropic_judgments_including_replacement"] == 0.101391
    assert costs["recorded_total_including_replacement_and_invalidated"] == 0.137604
    assert correction["invalidation_status"] == "INVALIDATED_PROTOCOL_MISMATCH"
    assert correction["unmeasured_events"][0]["type"] == "ASSUME"
