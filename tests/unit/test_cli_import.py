import pytest

import rabbit.cli


@pytest.mark.parametrize(
    "attr",
    [
        "cli",
        "console",
        "CONTEXT_SETTINGS",
        "Consumer",
        "Publisher",
        "consumer",
        "send_event",
    ],
)
def test_cli_module_attributes(attr):
    assert hasattr(rabbit.cli, attr)
