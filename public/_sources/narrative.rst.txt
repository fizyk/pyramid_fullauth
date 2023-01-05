Narrative
---------

Social login process
====================
When user clicks on 'Connect to facebook' link from any page he already is, he is redirect to social page to grant us access to his
social data. If this succeed, page redirects user to view with context 'velruse.AuthenticationComplete' and provides data from social page.
View register_social is fired and few scenarios are available. When user is already logged in, system connects this user's account with
social account. Same happens when user with email provided by social site exists.
When there is no user to connect him with social site, we need to create new user. When social site do not provide email of user
create user with fake email based on social user id and domain of social site, otherwise create user with data provived by social site.

When user is created or retrieved form session or database, then log him in and redirect to page he came from (or index).
Result of this action is always an activated, logged in user.
