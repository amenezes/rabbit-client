import pytest

from rabbit import constant, expo, fibo

DELAY_HEADER = {"x-delay": 1}


@pytest.mark.parametrize(
    "delay, expected",
    [
        (300000, 300000),
        (360000, 360000),
        (420000, 420000),
        (480000, 480000),
        (540000, 540000),
        (600000, 600000),
        (660000, 660000),
        (720000, 720000),
        (780000, 780000),
        (840000, 840000),
    ],
)
def test_constant_wait(delay, expected):
    for x in range(0, 11):
        current_delay = constant({"x-delay": delay}, delay)
        assert current_delay == expected


def test_constant_delay_update(monkeypatch):
    monkeypatch.setenv("CONSTANT_DELAY", "3000")
    expected = 3000
    for x in range(0, 11):
        if x == 5:
            monkeypatch.setenv("CONSTANT_DELAY", "1000")
            expected = 1000
        current_delay = constant({"x-delay": expected})
        assert current_delay == expected


@pytest.mark.parametrize(
    "delay, expected",
    [
        (300000, 360000),
        (360000, 420000),
        (420000, 480000),
        (480000, 540000),
        (540000, 600000),
        (600000, 660000),
        (660000, 720000),
        (720000, 780000),
        (780000, 840000),
        (840000, 900000),
    ],
)
def test_fibo_wait(delay, expected):
    current_delay = fibo({"x-delay": delay}, delay)
    assert current_delay == expected


def test_fibo_max_delay():
    current_delay = fibo({"x-delay": 86400000}, 1)
    assert current_delay == 86400000


@pytest.mark.parametrize(
    "delay, expected",
    [
        (300000, 600000),
        (600000, 1200000),
        (1200000, 2400000),
    ],
)
def test_expo_wait(delay, expected):
    assert expo({"x-delay": delay}, delay) == expected


def test_expo():
    delay = 300000
    for it in range(0, 11):
        current_delay = expo({"x-delay": delay}, delay)
        delay *= 2
        assert current_delay == delay


def test_expo_without_header():
    assert expo(None) == 600000


def test_expo_without_header_with_max_delay():
    delay = 1
    for it in range(10):
        current_delay = expo(None, delay=delay, max_delay=80)
        delay += current_delay
    assert current_delay == 80
