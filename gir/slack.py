'''
# gir-slack

A simple web-service to send slack messages.

## Routes

### /message

Sends a simple message to slack.

```json
{
    message
    icon_url
    username
    room
}
```

The following code sends a hello world to slack (Windows).

```bash
$ curl --request POST --data "{\"message\":\"hellow\"}" -H "Content-Type: application/json; charset=UTF-8"  http://localhost:5000/message
```
'''
from __future__ import unicode_literals
import os

from slackclient import SlackClient

from flask import request, render_template
from flask import Flask
from flask.ext.appconfig import AppConfig
from flask_debug import Debug
import six


def CreateApp(configfile=None):
    result = Flask(__name__)
    AppConfig(result, default_settings="config", configfile=configfile)
    Debug(result)
    return result


def GetConfig(config):
    result = app.config[config]
    if isinstance(result, six.text_type):
        result = os.path.expandvars(result)
    return result



app = CreateApp()



@app.route("/")
def index():
    import markdown2
    contents = markdown2.markdown(__doc__)
    return render_template(
        "index.html",
        title='gir-slack',
        contents=contents,
    )



@app.route("/message", methods=['GET', 'POST'])
def message():

    if request.method == 'GET':
        return 'TODO: Help message.'

    data = request.get_json()

    SlackMessage(
        data['message'],
        data.get('icon_url', '/static/slack.png'),
        data.get('username', 'gir-slack'),
        data.get('room', 'bos-ama'),
    )

    return 'OK'



def SlackMessage(message, icon_url=None, username=None, room=None):
    slack_token = GetConfig('SLACK_TOKEN')
    assert slack_token is not None, 'Please configure SLACK_TOKEN flask configuration.'

    icon_url = icon_url or GetConfig('STATIC_URL') + 'gir_stare.png'
    username = username or GetConfig('SLACK_USER') + '@' + GetConfig('SLACK_HOST')

    room = room or GetConfig('SLACK_ROOM')
    if room and not room.startswith('#'):
        room = '#' + room

    slack = SlackClient(slack_token)
    # print('LOG: chat.postMessage')
    # print('LOG: token=' + slack_token)
    # print('LOG: channel=' + room)
    # print('LOG: text=' + message)
    # print('LOG: icon_url=' + icon_url)
    # print('LOG: username=' + username)
    slack.api_call(
        'chat.postMessage',
        token=slack_token,
        channel=room,
        text=message,
        icon_url=icon_url,
        username=username,
    )



#---------------------------------------------------------------------------------------------------
# Entry Point
#---------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(GetConfig('PORT'))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
