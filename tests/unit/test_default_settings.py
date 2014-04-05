"""
Test for recognizing default settings.

Also helps to keeping them in line.
"""


def test_defaults(default_config):
    """Load defaults config for fullauth."""
    # Config should get created based on fullauth defaults
    assert 'fullauth' in default_config.registry['config']
    # csrf should be turned on by default
    assert default_config.registry['config']['fullauth']['check_csrf'] is True
    # also hashalg should be anything but not md5 by default.
    assert default_config.registry['config']['fullauth']['AuthTkt']['hashalg'] is not 'md5'
