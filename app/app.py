from __future__ import unicode_literals
from flask import Flask, request
from jsonsub import JsonSub, Remapping
from rq_dashboard import RQDashboard
from worker import Slack
import json
import os


app = Flask(__name__)
app.debug = True

RQDashboard(app)

slack = Slack()

CONFIG ={
    'stash' : dict(
        message = 'Commit on `repository.slug`',
        icon_url = 'https://developer.atlassian.com/imgs/stash.png',
        username = 'Stash',
    ),
    'jira' : dict(
        message = '<`issue.self`|`issue.key`>: `issue.fields.summary` [@`user.name`]',
        icon_url = 'https://developer.atlassian.com/imgs/jira.png',
        username = 'Jira',
    ),
    'message' : dict(
        message = '`message`',
        icon_url = 'http://static.tumblr.com/2qdysyt/AaTm73sce/gir_sitting.png',
        username = '`user`@`host`',
    ),
    'jenkins' : dict(
        message = 'Job `emoji` <https://eden.esss.com.br/jenkins/`url`|`name`> <`build.full_url`|#`build.number`>.',
        icon_url = 'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
        username = 'Jenkins',
        remapping = {
            'emoji' : {
                '__key'               : '`build.phase`, `build.status`',
                '__default'           : '(`build.phase`, `build.status`) :question:',
                'STARTED, '           : ':arrow_forward:',
                'FINALIZED, FAILURE'  : ':no_entry:',
                'FINALIZED, SUCCESS'  : ':white_check_mark:',
                'FINALIZED, ABORTED'  : ':warning:',
                'FINALIZED, UNSTABLE' : ':warning:',
            }
        },
        early_exit = {
            (
                '"`build.phase`" == "COMPLETED"',
                'Ignore COMPLETED events in favor of FINALIZED (after all post-build).',
                'OK',
            ),
        },
    ),
}

class Handler(object):

    def __init__(self, config):
        self.__config = config

    def __call__(self):
        return self.HandleIt(
            self.__config['message'],
            self.__config['icon_url'],
            self.__config['username'],
            self.__config.get('remapping', {}),
            self.__config.get('early_exit', {})
        )

    @classmethod
    def HandleIt(cls, message, icon_url, username, remapping={}, early_exit=[]):
        data = json.loads(request.data)

        # Create new values on data based on remapping dictionary.
        # Check Remapping function for more details.
        # Example:
        #   We use a different emoji depending on the combination of a build (jenkins) phase and status.
        for i_key, i_mapping in remapping.items():
            data[i_key] = Remapping(i_mapping, data)

        # Exits without sending the message to Slack under some conditions.
        for i_expression, i_description, i_result in early_exit:
            i_expression = JsonSub(i_expression, data)
            if eval(i_expression):
                return i_result

        # Sends the message (using queue)
        message = JsonSub(message, data)
        username = JsonSub(username, data)
        slack.Message(message, icon_url, username)

        return 'OK'



@app.route("/")
def index():
    return "Hello, from GIR!"


for i_route, i_config in CONFIG.items():
    handler = Handler(i_config)
    app.add_url_rule('/' + i_route, i_route, handler, methods=['POST'])


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
