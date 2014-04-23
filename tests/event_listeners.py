"""Event listener test app configurations."""
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from pyramid_fullauth.events import AlreadyLoggedIn


def include_events(config):
    """Dummy pyramid plugin including events."""
    config.add_route('event', '/event')
    config.scan('tests.event_listeners')
    config.add_subscriber(redirect_to_secret, AlreadyLoggedIn)


@view_config(route_name="event", renderer='json')
def event_view(request):
    """Dummy view."""
    return {'event', request.GET.get('event')}


def redirect_to_secret(event):
    """Redirect to event page with event name set as query event attribute."""
    raise HTTPFound(
        event.request.route_path(
            'event', _query=(('event', event.__class__.__name__),)
        ))
