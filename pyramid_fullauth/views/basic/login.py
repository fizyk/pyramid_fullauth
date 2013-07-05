# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import NO_PERMISSION_REQUIRED

from sqlalchemy.orm.exc import NoResultFound

from pyramid_basemodel import Session

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User
from pyramid_fullauth.events import BeforeLogIn
from pyramid_fullauth.events import AfterLogIn
from pyramid_fullauth.events import AlreadyLoggedIn


@view_defaults(permission=NO_PERMISSION_REQUIRED)
class LoginViews(BaseView):

    @view_config(route_name='login', renderer='pyramid_fullauth:resources/templates/login.mako')
    @view_config(route_name='login', request_method='POST', xhr=True, renderer="json")
    def login(self):
        '''
            Login action
        '''
        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''

        after = self.request.params.get('after') or self.request.referer
        return_dict = {'status': False,
                       'msg': self.request._('Login error', domain='pyramid_fullauth'),
                       'after': after, 'token': token}

        if authenticated_userid(self.request):
            try:
                self.request.registry.notify(AlreadyLoggedIn(self.request))
            except HTTPFound as redirect:
                if self.request.is_xhr:
                    return_dict['status'] = True
                    del return_dict['msg']
                    return_dict['after'] = redirect.location
                    return return_dict
                else:
                    return redirect

        # Code copied from alternative. Not yes implemented
        if self.request.method == 'POST':
            if self.check_csrf and token != self.request.POST.get('token'):
                return_dict['msg'] = self.request._('CSRF token did not match.',
                                                    domain='pyramid_fullauth')
                return return_dict

            email = self.request.POST.get('email', '')
            password = self.request.POST.get('password', '')
            try:
                user = Session.query(User).filter(User.email == email).one()
                try:
                    self.request.registry.notify(BeforeLogIn(self.request, user))
                except AttributeError as e:
                    return_dict['msg'] = str(e)
                    return return_dict

                if user.check_password(password):
                    try:
                        # if remember in POST set cookie timeout to one month
                        remember_me = self.request.POST.get('remember')
                        self.request.registry.notify(AfterLogIn(self.request, user))
                    except HTTPFound as redirect:
                        redirect_return = self.request.login_perform(
                            user, location=redirect.location, remember_me=remember_me)
                        if self.request.is_xhr:
                            return_dict['status'] = True
                            del return_dict['msg']
                            return_dict['after'] = redirect_return.location
                            return return_dict
                        else:
                            return redirect_return
                    except AttributeError as e:
                        return_dict['msg'] = str(e)
                        return return_dict
                    else:
                        redirect = self.request.login_perform(user, remember_me=remember_me)
                        if self.request.is_xhr:
                            return_dict['status'] = True
                            del return_dict['msg']
                            return_dict['after'] = redirect.location
                            return return_dict
                        else:
                            return redirect
                else:
                    return_dict['msg'] = self.request._('Wrong e-mail or password.',
                                                        domain='pyramid_fullauth')
                    return return_dict
            except NoResultFound:
                self.request.registry.notify(BeforeLogIn(self.request, None))

                return_dict['msg'] = self.request._('Wrong e-mail or password.',
                                                    domain='pyramid_fullauth')
                return return_dict
        else:
            self.request.registry.notify(BeforeLogIn(self.request, None))

        return_dict['status'] = True
        del return_dict['msg']
        return return_dict

    @view_config(route_name='logout')
    def logout(self):
        '''
            Logout method
        '''
        location = '/'
        if self.request.config.fullauth.redirects.logout:
            location = self.request.route_path(self.request.config.fullauth.redirects.logout)

        return HTTPFound(location=location, headers=forget(self.request))
