from __future__ import unicode_literals
import getpass
import socket



class Slack(object):

    SLACK_TOKEN = None
    SLACK_ROOM = '#bos-ama'
    SLACK_USER = getpass.getuser()
    SLACK_HOST = socket.gethostname()
    REDIS_SERVER = 'localhost'
    REDIS_PORT = 6379
    STATIC_URL = 'http://188.226.245.90/static/'

    def __init__(self, server=REDIS_SERVER, port=REDIS_PORT):
        from redis import Redis
        from rq import Queue
        connection = Redis(server, port)
        self.__queue = Queue(connection=connection)


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
