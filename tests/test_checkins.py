from wealth_os.checkins import DailyCEOCheckIn, score_checkin


def test_ceo_score_rewards_execution_and_leading_behaviors():
    checkin = DailyCEOCheckIn(
        commitments=["Call lender", "Source five opportunities", "Build acquisition memo"],
        completed_commitments=["Call lender", "Source five opportunities", "Build acquisition memo"],
        opportunity_creation="Source five owners and two brokers",
        deal_decision="Get leverage answer and kill deal if it fails",
        ownership_building="Complete acquisition memo",
        capital_allocation="Decide liquidity reserve target",
        relationship_deposit="Call broker with useful market data",
        health_energy="Train and protect sleep",
        kill_delegate_avoid="Delegate admin follow-up",
    )
    metrics = score_checkin(checkin)
    assert metrics.execution_rate == 100.0
    assert metrics.overall_score == 100.0


def test_empty_checkin_scores_zero():
    metrics = score_checkin(DailyCEOCheckIn())
    assert metrics.overall_score == 0.0
    assert metrics.execution_rate == 0.0
