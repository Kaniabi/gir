from __future__ import unicode_literals
from clikit.app import App
import getpass
import socket
import sys



app = App('girctl')


DEFAULT_ROOM = '#bos-ama'
DEFAULT_HOST = '188.226.245.90'
DEFAULT_PORT = 80

@app
def Message(console_, room=DEFAULT_ROOM, host=DEFAULT_HOST, port=DEFAULT_PORT, *message):
    '''
    Sends a message to slack.

    :param message: The message to send to slack.
    :param room: Defines the slack room to notify.
    '''
    _SlackMessage(console_, ' '.join(message), room=room, host=host, port=port)


@app
def Exec(console_, room=DEFAULT_ROOM, *cmd_line):
    '''
    Executes a command locally notifying slack after the command finishes.

    :param cmd_line: The command-line to execute.
    :param room: Defines the slack room to notify.
    '''
    from ben10.execute import Execute2

    cmd_line = ' '.join(cmd_line)

    output, retcode = Execute2(cmd_line.split(), pipe_stdout=False, shell=True)
    if retcode == 0:
        message = ':white_check_mark: $ %(cmd_line)s' % locals()
    else:
        message = ':warning: $ %(cmd_line)s' % locals()

    r = _SlackMessage(console_, message, room=room)
    console_.Print(r)


@app
def FillDb(console_):
    '''
    DEVELOPMENT
    '''
    from girapp import GirConfig

    database = GirConfig.GetDatabase('http://188.226.245.90:5984')
    if database is None:
        console_.Print("Error: Can't connect to couchdb server.")
        return 1

    database['circleci'] = dict(
            message = 'Job <`payload.build_url`|`payload.vcs_url`#`payload.branch`>',
            icon_url = 'circle.png',
            username = 'CircleCI',
        )

@app
def SendSample(console_, config_id, room=DEFAULT_ROOM, host=DEFAULT_HOST, port=DEFAULT_PORT, *message):
    '''
    DEVELOPMENT
    '''
    import os
    from ben10.filesystem import GetFileContents

    sample_filename = os.path.dirname(__file__) + '/../samples/' + config_id + '.json'
    if not os.path.isfile(sample_filename):
        console_.Print("Can't find sample file: %s" % sample_filename)
        return 1

    data = GetFileContents(sample_filename)

    r = _SlackData(console_, '/webhook/%s' % config_id, data, room=room, host=host, port=port)

    console_.Print(r)


@app
def Run(console_, name='gir'):
    '''
    '''
    from ben10.execute import Execute2
    output, retcode = Execute2(
        'docker rm %(name)s' % locals(),
        pipe_stdout=False,
    )
    output, retcode = Execute2(
        'docker run -p 80:80 -e SLACK_TOKEN=xoxb-3724390083-OaNvuxp0CbYdo0fiy5kPBcWE -e PORT=80 -e GIR_USER=gir -e GIR_HOST=docker --name %(name)s %(name)s' % locals(),
        pipe_stdout=False,
    )
    return retcode


def _SlackMessage(console_, message, room=DEFAULT_ROOM, host=DEFAULT_HOST, port=DEFAULT_PORT):
    USER = getpass.getuser()
    HOST = socket.gethostname()

    data = {
        'message' : message,
        'user' : USER,
        'host' : HOST,
        'room' : room,
    }
    return _SlackData(console_, '/message', data, room=room, host=host, port=port)


def _SlackData(console_, url, data, room=DEFAULT_ROOM, host=DEFAULT_HOST, port=DEFAULT_PORT):
    import json
    import requests

    headers = {
        'Content-type': 'application/json; charset=utf-8',
        'Accept': 'text/plain',
    }
    r = requests.post(
        'http://%(host)s:%(port)s%(url)s' % locals(),
        data=json.dumps(data),
        headers=headers
    )
    console_.Print('>' * 80)
    console_.Print(r.text)
    console_.Print('>' * 80)
    return r



if __name__ == '__main__':
    sys.exit(app.Main(sys.argv[1:]))