# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Fullauth's configuration module."""
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.interfaces import (
    IAuthorizationPolicy,
    IAuthenticationPolicy,
    IRootFactory,
    ISessionFactory,
    ISecurityPolicy,
)
from pyramid.session import JSONSerializer

from pyramid_fullauth.auth import groupfinder
from pyramid_fullauth.routing import predicates
from pyramid_fullauth.request import login_perform, logout, request_user

__version__ = "2.0.1"

from pyramid_fullauth.security import FullAuthSecurityPolicy


def build_fullauth_config(settings):
    """Build fullauth configuration dictionary."""
    fullauth_config = {
        "authtkt": {
            "secret": settings.get("fullauth.authtkt.secret", "fullauth_psst"),
            "hashalg": settings.get("fullauth.authtkt.hashalg", "sha512"),
        },
        "session": {
            "factory": "pyramid.session.SignedCookieSessionFactory",
            "settings": {"secret": "THATS_NOT_SECRET_ITS_A_SECRET"},
        },
        "register": {"password": {"require": True, "length_min": 6, "confirm": True}},
        "redirects": {"logout": False},
        "login": {"cookie_max_age": 2592000},  # 30 days
    }
    fullauth_settings = {s: settings[s] for s in settings if s.startswith("fullauth")}

    for setting_key, setting_value in fullauth_settings.items():
        key_parts = setting_key.split(".")
        key_length = len(key_parts)

        if key_parts[1] == "register" and key_length == 4:
            if key_parts[2] == "password":
                fullauth_config["register"]["password"][key_parts[3]] = setting_value
        elif key_parts[1] == "authtkt" and key_length == 3:
            fullauth_config["authtkt"][key_parts[2]] = setting_value
        elif key_parts[1] == "login" and key_length == 3:
            fullauth_config["login"][key_parts[2]] = setting_value
        elif key_parts[1] == "session":
            if key_parts[2] == "factory" and key_length == 3:
                fullauth_config["session"]["factory"] = setting_value
            elif key_parts[2] == "settings" and key_length == 4:
                fullauth_config["session"]["settings"] = setting_value
        elif key_parts[1] == "social" and key_length == 4:
            if "social" not in fullauth_config:
                fullauth_config["social"] = {}
            if key_parts[2] not in fullauth_config["social"]:
                fullauth_config["social"][key_parts[2]] = {}
            fullauth_config["social"][key_parts[2]][key_parts[3]] = setting_value

    return fullauth_config


def includeme(configurator: Configurator) -> None:
    """
    Configure pyramid_fullauth on application.

    :param pyramid.configurator.Configurator configurator: pyramid's configurator object
    """
    configurator.include("pyramid_localize")
    configurator.include("pyramid_mako")
    fullauth_settings = build_fullauth_config(configurator.get_settings())
    configurator.registry["fullauth"] = fullauth_settings

    if configurator.registry.queryUtility(ISecurityPolicy) is None:
        configurator.set_security_policy(FullAuthSecurityPolicy(fullauth_settings["authtkt"]))

    # register root factory, only if not set already
    if configurator.registry.queryUtility(IRootFactory) is None:
        configurator.set_root_factory("pyramid_fullauth.auth.BaseACLRootFactoryMixin")

    # register session factory, only, if not already registered
    if configurator.registry.queryUtility(ISessionFactory) is None:
        # loading and setting session factory
        # first, divide provided path for module, and factory name
        module, factory = fullauth_settings["session"]["factory"].rsplit(".", 1)
        # import session module first
        session_module = __import__(module, fromlist=[module])
        # get the  factory class
        session_factory = getattr(session_module, factory)

        session_settings = fullauth_settings["session"]["settings"].copy()
        if "serializer" not in session_settings:
            session_settings["serializer"] = JSONSerializer()

        # set the new session factory
        configurator.set_session_factory(session_factory(**session_settings))

    # add predicates
    configurator.add_route_predicate("user_path_hash", predicates.UserPathHashRoutePredicate)

    # add routes
    configurator.add_route(name="login", pattern="/login")
    configurator.add_route(name="logout", pattern="/logout")
    configurator.add_route(name="register", pattern="/register")
    configurator.add_route(name="register:activate", pattern="/register/activate/{hash}")
    configurator.add_route(name="password:reset", pattern="/password/reset")
    configurator.add_route(
        name="password:reset:continue",
        pattern="/password/reset/{hash}",
        user_path_hash="reset_key",
    )
    configurator.add_route(name="email:change", pattern="/email/change")
    configurator.add_route(
        name="email:change:continue",
        pattern="/email/change/{hash}",
        user_path_hash="email_change_key",
    )
    # scan base views
    configurator.scan("pyramid_fullauth.views.basic")

    # check for the social.
    # If social is not available, we will not turn it on!
    if "social" in fullauth_settings:
        # Velruse init (for social auth)

        # scan social views
        configurator.scan("pyramid_fullauth.views.social")
        providers = fullauth_settings["social"]
        for provider in providers:
            # Ugly hack for using google oauth2, not OpenID + Oauth2 from google
            provider_settings = fullauth_settings["social"][provider]
            if provider == "google":  # pragma: no cover
                provider = "google_oauth2"

            configurator.include("velruse.providers." + provider)
            getattr(configurator, f"add_{provider}_login")(**provider_settings)

    # we'll add some request methods:
    configurator.add_request_method(login_perform, name="login_perform")
    configurator.add_request_method(logout, name="logout")
    configurator.add_request_method(request_user, name="user", reify=True)
