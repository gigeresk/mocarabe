import collections
import datetime
import types

from mocarabe.cad.scheduler import SchedulerStrategy
from mocarabe.device import Device


class FakeScheduler(SchedulerStrategy):
    """Infeasible until the device has at least min_channels channels"""

    def __init__(self, min_channels):
        self.min_channels = min_channels
        self.tried = []

    def schedule(self, device, *args):
        self.tried.append(device.physical_channels)
        if device.physical_channels < self.min_channels:
            raise AssertionError("infeasible")
        return "scheduled", 0, 0


def run(scheduler, tmp_path, monkeypatch, channels=2, max_channels=None):
    monkeypatch.chdir(tmp_path)  # the scheduler writes log/ and results/ here
    device = Device(2, 2, channels, 1, 1, 2, 1, "", 5, 2, 1, 4, 1)
    file_helper = types.SimpleNamespace(
        log_file=str(tmp_path / "log.csv"),
        benchmark_name="fake",
        netlist_filepath="",
        schedule_filepath="",
    )
    result = scheduler.run_scheduling_with_timeout(
        device,
        None,
        datetime.timedelta(0),
        file_helper,
        collections.Counter(),
        "-",
        sched_time=10,
        max_channels=max_channels,
    )
    return result, device


def test_max_channels_raises_c_until_schedulable(tmp_path, monkeypatch):
    scheduler = FakeScheduler(min_channels=4)
    result, device = run(scheduler, tmp_path, monkeypatch, max_channels=6)
    assert result == "scheduled"
    assert scheduler.tried == [2, 3, 4]
    assert device.physical_channels == 4
    assert device.noc_pipelining_stages == 2


def test_max_channels_gives_up_at_limit(tmp_path, monkeypatch):
    scheduler = FakeScheduler(min_channels=5)
    result, device = run(scheduler, tmp_path, monkeypatch, max_channels=3)
    assert result is None
    assert scheduler.tried == [2, 3]


def test_max_channels_searches_past_legacy_retry_count(tmp_path, monkeypatch):
    scheduler = FakeScheduler(min_channels=12)
    result, _ = run(scheduler, tmp_path, monkeypatch, max_channels=12)
    assert result == "scheduled"
    assert scheduler.tried == list(range(2, 13))
