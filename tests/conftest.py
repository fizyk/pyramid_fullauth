
from mock import Mock

import pytest
import transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def web_request():
    request = Mock()
    config = Mock()
    config.configure_mock(
        **{'fullauth.register.password':
            {'length_min': 8, 'confirm': True},
            'POST': {'confirm_password': '987654321'}
           }
    )

    def _(message, *args, **kwargs):
        return message
    request._ = Mock(side_effect=_)
    request.configure_mock(
        **{'registry': {'config': config}}
    )

    return request


@pytest.fixture(scope='function')
def db_session(request):
    from pyramid_fullauth.models import Base

    connection = 'sqlite://'

    engine = create_engine(connection, echo=False)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    def destroy():
        Base.metadata.drop_all(engine)
        session.close()

    request.addfinalizer(destroy)

    return session


@pytest.fixture
def user(db_session):

    from pyramid_fullauth.models import User
    user = User(username='u1',
                password='password1',
                email='email@example.com',
                address_ip='127.0.0.1')
    db_session.add(user)
    transaction.commit()
    return user
