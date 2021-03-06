from django.conf import settings
from oauth_tokens.api import ApiAbstractBase, Singleton
from oauth_tokens.models import AccessToken
from tweepy import TweepError as TwitterError
import tweepy

__all__ = ['api_call', 'TwitterError']

TWITTER_CLIENT_ID = getattr(settings, 'OAUTH_TOKENS_TWITTER_CLIENT_ID', None)
TWITTER_CLIENT_SECRET = getattr(settings, 'OAUTH_TOKENS_TWITTER_CLIENT_SECRET', None)


class TwitterApi(ApiAbstractBase):

    __metaclass__ = Singleton

    provider = 'twitter'
    error_class = TwitterError

    def get_consistent_token(self):
        return getattr(settings, 'TWITTER_API_ACCESS_TOKEN', None)

    def get_api(self, **kwargs):
        token = self.get_token(**kwargs)

        delimeter = AccessToken.objects.get_token_class(self.provider).delimeter
        auth = tweepy.OAuthHandler(TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET)

        token = token.split(delimeter)
        try:
            auth.access_token = tweepy.oauth.OAuthToken(token[0], token[1])
        except AttributeError:
            # dev version
            auth.access_token = token[0]
            auth.access_token_secret = token[1]

        return tweepy.API(auth)

    def get_api_response(self, *args, **kwargs):
        return getattr(self.api, self.method)(*args, **kwargs)

    def handle_error_code(self, e, *args, **kwargs):
        e.code = e[0][0]['code']
        return super(TwitterApi, self).handle_error_code(e, *args, **kwargs)

#     def handle_error_code_63(self, e, *args, **kwargs):
# User has been suspended.
#         self.refresh_tokens()
#         return self.repeat_call(*args, **kwargs)


def api_call(*args, **kwargs):
    api = TwitterApi()
    return api.call(*args, **kwargs)
