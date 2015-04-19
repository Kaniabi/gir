from __future__ import unicode_literals
from clikit.app import App
import getpass
import socket
import sys



app = App('girctl')


DEFAULT_ROOM = '#bos-ama'


@app
def Message(console_, room=DEFAULT_ROOM, *message):
    '''
    Sends a message to slack.

    :param message: The message to send to slack.
    :param room: Defines the slack room to notify.
    '''
    _SlackMessage(' '.join(message), room=room)


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

    r = _SlackMessage(message, room=room)
    console_.Print(r)


@app
def Build(console_, name='gir'):
    '''
    '''
    from ben10.execute import Execute2
    output, retcode = Execute2(
        'docker build --rm -t %(name)s:latest' % locals(),
        pipe_stdout=False,
    )
    return retcode


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


def _SlackMessage(message, room=DEFAULT_ROOM, host='188.226.245.90', port=80):
    import json
    import requests

    USER = getpass.getuser()
    HOST = socket.gethostname()

    data = {
        'message' : message,
        'user' : USER,
        'host' : HOST,
        'room' : room,
    }
    headers = {
        'Content-type': 'application/json; charset=utf-8',
        'Accept': 'text/plain'
    }
    r = requests.post(
        'http://%(host)s:%(port)s/message' % locals(),
        data=json.dumps(data).decode('UTF-8'),
        headers=headers
    )
    print '>' * 80
    print r.text
    print '>' * 80
    return r



if __name__ == '__main__':
    sys.exit(app.Main(sys.argv[1:]))
