import pytest

from tests.utils import create_user


@pytest.fixture()
def db_with_user(db):
    create_user(db, {'username': 'u1',
                     'password': 'password1',
                     'email': 'email@example.com',
                     'address_ip': '127.0.0.1'})
    return db
