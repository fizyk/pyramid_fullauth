"""Most of the fixtures needed."""
from mock import Mock
import pytest

import transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool
from zope.sqlalchemy import register

from pyramid.compat import text_type
from pytest_pyramid import factories
import pyramid_basemodel


@pytest.fixture
def web_request():
    """Test web request for views testing."""
    request = Mock()
    config = Mock()
    config.configure_mock(**{
        'POST': {'confirm_password': '987654321'}
    })

    fullauth_config = {
        "register": {
            "password": {
                "length_min": 8,
                "confirm": True
            }
        }
    }

    def _(message, *_, **__):
        return message
    request._ = Mock(side_effect=_)
    request.configure_mock(**{"registry": {"config": config, "fullauth": fullauth_config}})

    return request


@pytest.fixture(scope='function', params=['sqlite', 'mysql', 'postgresql'])
def db_session(request):
    """Session for SQLAlchemy."""
    from pyramid_fullauth.models import Base  # pylint:disable=import-outside-toplevel

    if request.param == 'sqlite':
        connection = 'sqlite:///fullauth.sqlite'
    elif request.param == 'mysql':
        request.getfixturevalue('mysql')  # takes care of creating database
        connection = 'mysql+mysqldb://root:@127.0.0.1:3307/tests?charset=utf8'
    elif request.param == 'postgresql':
        request.getfixturevalue('postgresql')  # takes care of creating database
        connection = 'postgresql+psycopg2://postgres:@127.0.0.1:5433/tests'

    engine = create_engine(connection, echo=False, poolclass=NullPool)
    pyramid_basemodel.Session = scoped_session(sessionmaker())
    register(pyramid_basemodel.Session)
    pyramid_basemodel.bind_engine(
        engine, pyramid_basemodel.Session, should_create=True, should_drop=True)

    def destroy():
        transaction.commit()
        Base.metadata.drop_all(engine)

    request.addfinalizer(destroy)

    return pyramid_basemodel.Session


@pytest.fixture
def user(db_session):  # pylint:disable=redefined-outer-name
    """Test user fixture."""
    from pyramid_fullauth.models import User  # pylint:disable=import-outside-toplevel
    from tests.tools import DEFAULT_USER  # pylint:disable=import-outside-toplevel
    new_user = User(**DEFAULT_USER)
    db_session.add(new_user)
    transaction.commit()
    return new_user


@pytest.fixture
def active_user(user, db_session):  # pylint:disable=redefined-outer-name
    """Active user."""
    user = db_session.merge(user)
    user.is_active = True
    transaction.commit()
    return user


@pytest.fixture(params=[
    # (an @ character must separate the local and domain parts)
    text_type('Abc.example.com'),
    # (character dot(.) is last in local part)
    text_type('Abc.@example.com'),
    # (character dot(.) is double)
    text_type('Abc..123@example.com'),
    # (only one @ is allowed outside quotation marks)
    text_type('A@b@c@example.com'),
    # (none of the special characters in this local part is allowed outside quotation marks)
    text_type('a"b(c)d,e:f;g<h>i[j\\k]l@example.com'),
    # (quoted strings must be dot separated, or the only element making up the local-part)
    text_type('just"not"right@example.com'),
    # (spaces, quotes, and backslashes may only exist when within quoted strings and preceded by a backslash)
    text_type('this is"not\\allowed@example.com'),
    # (even if escaped (preceded by a backslash), spaces, quotes, and backslashes must still be contained by quotes)
    text_type('this\\ still\"not\\allowed@example.com'),
    text_type('bad-mail'),
])
def invalid_email(request):
    """Parametrized fixture with all the incorrect emails."""
    return request.param


# pylint:disable=invalid-name
default_config = factories.pyramid_config({
    'pyramid.includes': [
        'pyramid_tm',
        'pyramid_fullauth'
    ]
})


default_app = factories.pyramid_app('default_config')


extended_config = factories.pyramid_config({
    'pyramid.includes': [
        'pyramid_tm',
        'pyramid_fullauth',
        'tests.tools.include_views'
    ]
})


extended_app = factories.pyramid_app('extended_config')


short_config = factories.pyramid_config({
    "fullauth.authtkt.timeout": 2,
    "fullauth.authtkt.reissue_time": 0.2,
    'pyramid.includes': [
        'pyramid_tm',
        'pyramid_fullauth',
        'tests.tools.include_views'
    ]
})


short_app = factories.pyramid_app('short_config')


social_config = factories.pyramid_config({
    "fullauth.social.facebook.consumer_key": "173883269419608",
    "fullauth.social.facebook.consumer_secret": "f8421ff0856d742fc10aa764537be181",
    "fullauth.social.facebook.scope": "email,offline_access",
    'pyramid.includes': [
        'pyramid_tm',
        'pyramid_fullauth',
        'tests.tools.include_views'
    ]
})


social_app = factories.pyramid_app('social_config')


authable_config = factories.pyramid_config({
    'env': 'login',
    'pyramid.includes': [
        'pyramid_tm',
        'pyramid_fullauth',
        'tests.tools.include_views'
    ]
})


authable_app = factories.pyramid_app('authable_config')


nopassconfirm_config = factories.pyramid_config({
    "fullauth.register.password.require": True,
    "fullauth.register.password.confirm": False,
    'env': 'login',
    'pyramid.includes': [
        'pyramid_tm',
        'pyramid_fullauth',
        'tests.tools.include_views'
    ]
})


nopassconfirm_app = factories.pyramid_app('nopassconfirm_config')


nopassregister_config = factories.pyramid_config({
    "fullauth.register.password.require": False,
    'env': 'login',
    'pyramid.includes': [
        'pyramid_tm',
        'pyramid_fullauth',
        'tests.tools.include_views'
    ]
})


nopassregister_app = factories.pyramid_app('nopassregister_config')
# pylint:enable=invalid-name
