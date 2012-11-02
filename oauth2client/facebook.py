"""Facebook's version of oAuth"""
from .baseserver import *
from collections import namedtuple as _namedtuple

class BearerToken(BearerToken):
    apply_req = BearerToken.apply_req_query

_scope = """
user_about_me
friends_about_me
user_activities
friends_activities
user_birthday
friends_birthday
user_checkins
friends_checkins
user_education_history
friends_education_history
user_events
friends_events
user_groups
friends_groups
user_hometown
friends_hometown
user_interests
friends_interests
user_likes
friends_likes
user_location
friends_location
user_notes
friends_notes
user_photos
friends_photos
user_questions
friends_questions
user_relationships
friends_relationships
user_relationship_details
friends_relationship_details
user_religion_politics
friends_religion_politics
user_status
friends_status
user_subscriptions
friends_subscriptions
user_videos
friends_videos
user_website
friends_website
user_work_history
friends_work_history
email
read_friendlists
read_insights
read_mailbox
read_requests
read_stream
xmpp_login
ads_management
create_event
manage_friendlists
manage_notifications
user_online_presence
friends_online_presence
publish_checkins
publish_stream
rsvp_event
publish_actions
user_actions.music
friends_actions.music
user_actions.news
friends_actions.news
user_actions.video
friends_actions.video
user_games_activity
friends_games_activity
manage_pages
""".split()

class FacebookOAuth2(OAuth2Server):
    name = "facebook"
    auth_endpoint = "https://facebook.com/dialog/oauth"
    token_endpoint = "https://graph.facebook.com/oauth/access_token"
    scope = Scope(filter(None,map(str.strip, _scope)))
    _Response = _namedtuple("_Response", ("text", "status_code"))

    def token_resp2token(self, resp):
        from urllib.parse import parse_qs
        import json
        text = dict((k, v[0]) for k,v in parse_qs(resp.text).items())
        text["token_type"] = "bearer"
        x = self._Response(text = json.dumps(text), status_code = resp.status_code)
        return super().token_resp2token(x)
