from __future__ import unicode_literals


def GetConfig(name):
    import os
    import default_config

    result = os.environ.get('GIR_' + name)
    if result is not None:
        return result
    return getattr(default_config, name)


class Slack(object):

    SLACK_TOKEN = GetConfig('SLACK_TOKEN')
    SLACK_ROOM = GetConfig('SLACK_ROOM')
    SLACK_USER = GetConfig('SLACK_USER')
    SLACK_HOST = GetConfig('SLACK_HOST')
    REDIS_HOST = GetConfig('REDIS_HOST')
    REDIS_PORT = GetConfig('REDIS_PORT')
    REDIS_DB = GetConfig('REDIS_DB')
    REDIS_PASSWORD = GetConfig('REDIS_PASSWORD')
    STATIC_URL = GetConfig('STATIC_URL')


    def __init__(self):
        from rq import Queue

        connection = self.CreateConnection()
        self.__queue = Queue(connection=connection)


    @classmethod
    def CreateConnection(cls):
        from redis import Redis

        return Redis(
            host=cls.REDIS_HOST,
            port=cls.REDIS_PORT,
            db=cls.REDIS_DB,
            password=cls.REDIS_PASSWORD
        )


    def Message(self, message, icon_url=None, username=None, room=SLACK_ROOM):
        import sys
        if sys.platform == 'win32':
            execute = lambda f, m, i, u, r: f(m,i,u,r)
        else:
            execute = self.__queue.enqueue
        execute(Slack.SendMessage, message, icon_url, username, room)


    @classmethod
    def StaticResource(cls, filename):
        return cls.STATIC_URL + filename


    @classmethod
    def SendMessage(cls, message, icon_url=None, username=None, room=SLACK_ROOM):
        from slackclient import SlackClient

        assert cls.SLACK_TOKEN is not None, 'Please configure SLACK_TOKEN flask configuration.'

        icon_url = icon_url or cls.StaticResource('gir_stare.png')
        username = username or '%s@%s' % (cls.SLACK_USER, cls.SLACK_HOST)

        slack = SlackClient(cls.SLACK_TOKEN)
        slack.api_call(
            'chat.postMessage',
            token=cls.SLACK_TOKEN,
            channel=room,
            text=message,
            icon_url=icon_url,
            username=username,
        )
