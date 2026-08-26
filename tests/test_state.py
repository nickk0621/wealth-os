import pytest
from pydantic import ValidationError

from wealth_os.state import DailyCheckIn, OperatingState


def test_default_operating_state_is_empty_and_valid():
    state = OperatingState()
    assert state.goals == []
    assert state.deals == []
    assert state.daily_checkins == []


def test_daily_checkin_validates_energy_range():
    checkin = DailyCheckIn(energy=8, sleep_hours=7.5, deep_work_hours=2.0)
    assert checkin.energy == 8

    with pytest.raises(ValidationError):
        DailyCheckIn(energy=11)
