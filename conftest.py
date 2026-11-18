"""Root pytest configuration."""


def pytest_configure(config):
    """Anchor default basetemp to the repository root regardless of CWD."""
    if config.option.basetemp is None:
        config.option.basetemp = str(config.rootpath / ".pytest_tmp")
