

def test_defaults(base_app):
    '''Load defaults config for fullauth'''

    # Config should get created based on fullauth defaults
    assert 'fullauth' in base_app.config.registry['config']
