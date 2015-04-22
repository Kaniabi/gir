from __future__ import unicode_literals



def StaticResource(filename):
    import os
    STATIC_URL = os.environ.get('GIR_STATIC_URL', 'http://188.226.245.90/static/')
    return STATIC_URL + filename


def SendMessage(message, icon_url=None, username=None, room=None):
    from slackclient import SlackClient
    import getpass
    import os
    import socket

    TOKEN = os.environ.get('SLACK_TOKEN')
    assert TOKEN is not None, 'Please configure SLACK_TOKEN environment variable.'
    USER = os.environ.get('GIR_USER', getpass.getuser())
    HOST = os.environ.get('GIR_HOST', socket.gethostname())
    icon_url = icon_url or StaticResource('gir_stare.png')
    username = username or '%s@%s' % (USER, HOST)
    room = room or os.environ.get('SLACK_ROOM', '#general')

    slack = SlackClient(TOKEN)
    slack.api_call(
        'chat.postMessage',
        token=TOKEN,
        channel=room,
        text=message,
        icon_url=icon_url,
        username=username,
    )


class Slack(object):

    def __init__(self):
        from redis import Redis
        from rq import Queue
        import os
        redis_server = os.environ.get("REDIS_SERVER", 'localhost')
        redis_port = int(os.environ.get("REDIS_PORT", 6379))
        redis_connection = Redis(redis_server, redis_port)
        self.__queue = Queue(connection=redis_connection)

    def Message(self, message, icon_url=None, username=None, room=None):
        self.__queue.enqueue(SendMessage, message, icon_url, username, room)

