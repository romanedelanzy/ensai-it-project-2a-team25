from unittest.mock import MagicMock

from service.recommandation_service import RecommandationService


def test_get_reliability_score_uses_current_score():
    reliability_service = MagicMock()
    reliability_service.reliability_current_score.return_value = 0.82
    service = RecommandationService(
        station_dao=MagicMock(),
        station_status_dao=MagicMock(),
        reliability_service=reliability_service,
    )

    assert service._get_reliability_score("ST001") == 0.82
    reliability_service.reliability_current_score.assert_called_once_with("ST001")
