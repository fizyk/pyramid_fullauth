import transaction

from pyramid_fullauth.models import User

user_data = {
    'email': u'email@example.com',
    'password': u'Password',
    'address_ip': u'0.0.0.0',
}


def create_user(session, user_data=user_data):
    user = User(**user_data)
    session.add(user)
    transaction.commit()
