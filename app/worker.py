from __future__ import unicode_literals



def SendMessage(message, icon_url=None, username=None, room=None):
    from slackclient import SlackClient
    import getpass
    import os
    import socket

    TOKEN = os.environ.get('SLACK_TOKEN')
    assert TOKEN is not None, 'Please configure SLACK_TOKEN environment variable.'
    USER = os.environ.get('GIR_USER', getpass.getuser())
    HOST = os.environ.get('GIR_HOST', socket.gethostname())
    icon_url = icon_url or 'http://files.gamebanana.com/img/ico/sprays/gir_stare.png'
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
        self.__queue = Queue(connection=Redis())

    def Message(self, message, icon_url=None, username=None, room=None):
        self.__queue.enqueue(SendMessage, message, icon_url, username, room)

