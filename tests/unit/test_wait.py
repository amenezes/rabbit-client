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
    assert constant({"x-delay": delay}, delay) == expected


def test_constant_uses_default_when_no_delay_arg():
    assert constant(None) == 300000


def test_constant_ignores_env_vars(monkeypatch):
    monkeypatch.setenv("CONSTANT_DELAY", "3000")
    assert constant(None) == 300000
    monkeypatch.setenv("CONSTANT_DELAY", "1000")
    assert constant(None) == 300000


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


def test_expo_doubles_delay():
    assert expo(None, delay=300000) == 600000


def test_expo_with_header_uses_header_value():
    assert expo({"x-delay": 5000}, delay=300000) == 10000


def test_expo_without_header():
    assert expo(None) == 600000


def test_expo_factor_zero():
    assert expo(None, delay=300000, factor=0) == 0


@pytest.mark.parametrize(
    "delay,max_delay,expected",
    [
        (200, 80, 80),
        (40, 80, 80),
        (39, 80, 78),
        (1, 80, 2),
    ],
)
def test_expo_respeita_max_delay(delay, max_delay, expected):
    assert expo(None, delay=delay, max_delay=max_delay) == expected
