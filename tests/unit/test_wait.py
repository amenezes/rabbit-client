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
    ],
)
def test_expo_wait(delay, expected):
    current_delay = expo({"x-delay": delay}, delay)
    assert current_delay == expected


def test_expo():
    init_delay = 300000
    for it in range(0, 11):
        current_delay = expo({"x-delay": init_delay}, init_delay)
        init_delay = init_delay * 2
        assert current_delay == init_delay


def test_expo_without_header():
    current_delay = expo(None)
    assert current_delay == 600000


def test_expo_without_header_with_max_delay():
    initial_delay = 1
    for it in range(0, 10):
        initial_delay = expo(None, initial_delay, max_delay=80)
        final_delay = initial_delay
    assert final_delay == 80