"""Email change views."""

import http

import pytest
import transaction
from sqlalchemy.orm.exc import NoResultFound

from pyramid_fullauth.models import User
from tests.tools import DEFAULT_USER, authenticate


def test_email_view_not_logged(default_app):
    """Try to access email change view anonymously."""
    app = default_app
    res = app.get("/email/change")
    assert res.status_code == http.HTTPStatus.FOUND
    assert res.location == "http://localhost/login?after=%2Femail%2Fchange"


@pytest.mark.usefixtures("active_user")
def test_email_view_logged(db_session, default_app):
    """Simple get for change email view."""
    app = default_app
    db_session.close()
    # Session are de-syncronised

    # login user
    authenticate(app)

    res = app.get("/email/change")
    assert res.status_code == http.HTTPStatus.OK
    assert res.form
    assert res.form["email"]


@pytest.mark.usefixtures("active_user")
def test_email_valid(db_session, default_app):
    """Change email with valid data."""
    app = default_app

    authenticate(app)
    email = DEFAULT_USER["email"]
    new_email = "email@email.com"

    user = db_session.query(User).filter(User.email == email).one()

    res = app.get("/email/change")
    form = res.form
    form["email"] = new_email
    res = form.submit()
    assert res

    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    assert user.new_email == new_email
    assert user.email == email
    assert user.email_change_key is not None


@pytest.mark.usefixtures("active_user")
def test_email_valid_xhr(db_session, default_app):
    """Change email with valid data."""
    app = default_app

    authenticate(app)
    email = DEFAULT_USER["email"]
    new_email = "email@email.com"

    user = db_session.query(User).filter(User.email == email).one()

    res = app.get("/email/change")
    res = app.post(
        "/email/change",
        {"csrf_token": res.form["csrf_token"].value, "email": new_email},
        xhr=True,
    )
    assert res.json["status"] is True

    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    assert user.new_email == new_email
    assert user.email == email
    assert user.email_change_key is not None


@pytest.mark.usefixtures("db_session", "active_user")
def test_wrong_email(default_app, invalid_email):
    """Change email with incorrect email."""
    app = default_app
    # login user
    authenticate(app)

    res = app.get("/email/change")
    form = res.form
    form["email"] = invalid_email
    res = form.submit()
    assert "Error! Incorrect e-mail format" in res


@pytest.mark.usefixtures("db_session", "active_user")
def test_empty_email(default_app):
    """Try to change email with empty value."""
    app = default_app
    # login user
    authenticate(app)

    res = app.get("/email/change")
    form = res.form
    form["email"] = ""
    res = form.submit()
    assert "Error! E-mail is empty" in res


@pytest.mark.usefixtures("active_user")
def test_existing_email(db_session, default_app):
    """Try to change email to existing one email."""
    # add other user
    existing_email = "existing@email.eg"
    db_session.add(
        User(
            email=existing_email,
            password="somepassword",
            address_ip=DEFAULT_USER["address_ip"],
        )
    )
    transaction.commit()
    # login user
    authenticate(default_app)

    # submit request!
    res = default_app.get("/email/change")
    form = res.form
    form["email"] = existing_email
    res = form.submit()
    assert "Error! User with this email exists" in res


@pytest.mark.usefixtures("active_user")
def test_email_proceed(db_session, default_app):
    """Confirm email change view."""
    app = default_app
    # login user
    authenticate(app)

    email = DEFAULT_USER["email"]
    user = db_session.query(User).filter(User.email == email).one()

    new_email = "email2@email.com"
    user.set_new_email(new_email)
    transaction.commit()

    user = db_session.merge(user)
    res = app.get("/email/change/" + user.email_change_key)
    assert res.status_code == http.HTTPStatus.SEE_OTHER

    with pytest.raises(NoResultFound):
        # there is no user with old email
        db_session.query(User).filter(User.email == email).one()

    user = db_session.query(User).filter(User.email == new_email).one()
    assert not user.email_change_key


@pytest.mark.usefixtures("active_user")
def test_email_proceed_wrong_key(db_session, default_app):
    """Try to confirm email change view with wrong key."""
    app = default_app
    # login user
    authenticate(app)

    email = DEFAULT_USER["email"]
    user = db_session.query(User).filter(User.email == email).one()

    new_email = "email2@email.com"
    user.set_new_email(new_email)
    transaction.commit()

    user = db_session.merge(user)
    res = app.get("/email/change/" + user.email_change_key + "randomchars", status=404)
    assert res.status_code == http.HTTPStatus.NOT_FOUND
