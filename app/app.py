from __future__ import unicode_literals
from flask import Flask, request, render_template
from rq_dashboard import RQDashboard
from flask_debug import Debug
from worker import Slack, StaticResource
import os


app = Flask(__name__)
app.debug = True

RQDashboard(app)
Debug(app)

slack = Slack()

class GirConfig(object):
    '''
    Provides gir webhook configurations to the application.
    '''

    CONFIG ={
        'stash' : dict(
            message = '`repository.slug`#`refChanges[0].refId`: `changesets.values[0].toCommit.displayId`: `changesets.values[0].toCommit.message`',
            icon_url = 'stash.png',
            username = '`changesets.values[0].toCommit.author.emailAddress`',
        ),
        'jira' : dict(
            message = '<`issue.self`|`issue.key`>: `issue.fields.summary`',
            icon_url = 'jira.png',
            username = '`user.name`@esss.com.br',
        ),
        'message' : dict(
            message = '`message`',
            icon_url = 'gir_sitting.png',
            username = '`user`@esss.com.br',
        ),
        'circleci' : dict(
            message = 'Job <`payload.build_url`|`payload.vcs_url`#`payload.branch`>',
            icon_url = 'circle.png',
            username = 'CircleCI',
        ),
        'github' : dict(
            message = 'Commit on <`repository.url`|`repository.full_name`>',
            icon_url = 'github.png',
            username = '`pusher.email`',
        ),
        'jenkins' : dict(
            message = 'Job `emoji` <https://eden.esss.com.br/jenkins/`url`|`name`> <`build.full_url`|#`build.number`>.',
            icon_url = 'jenkins.png',
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
            early_exit = [
                (
                    '"`build.phase`" == "COMPLETED"',
                    'Ignore COMPLETED events in favor of FINALIZED (after all post-build).',
                    'OK',
                ),
            ],
        ),
    }

    @classmethod
    def GetDatabase(
        cls,
        server = os.environ.get('COUCHDB_SERVER'),
        database = os.environ.get('COUCHDB_DATABASE', 'gir-config'),
    ):
        if server is None:
            return None

        from couchdb.client import Server
        couchdb_server = Server(server)
        return couchdb_server[database]


    @classmethod
    def Get(cls, config_id):

        database = cls.GetDatabase()

        result = None
        if database is not None:
            result = database.get(config_id)

        # Fallback from default/local configuration (for now).
        # This is expected for testing.
        if result is None:
            result = cls.CONFIG.get(config_id)
        return result



class Handler(object):

    def __init__(self, config):
        self.__config = config

    def __call__(self):
        return self.HandleIt(
            self.__config['message'],
            self.__config['icon_url'],
            self.__config['username'],
            self.__config.get('remapping', {}),
            self.__config.get('early_exit', [])
        )

    @classmethod
    def HandleIt(cls, message, icon_url, username, remapping={}, early_exit=[]):
        from jsonsub import JsonSub, Remapping

        data = request.json

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
        icon_url = StaticResource(icon_url)
        icon_url = cls.GravatarUrl(username, default=icon_url)
        slack.Message(message, icon_url, username)

        return 'OK'


    @classmethod
    def GravatarUrl(cls, email, size=42, default=None):
        import hashlib
        from collections import OrderedDict
        from six.moves.urllib.parse import urlencode

        result = "http://www.gravatar.com/avatar/" + hashlib.md5(email.encode('ascii').lower()).hexdigest() + "?"

        params = OrderedDict()
        if default is not None:
            params['d'] = default
        params['s'] = str(size)
        result = result + urlencode(params)
        return result


@app.route("/")
def index():
    return render_template('index.html', name=name)


@app.route("/webhook/<config_id>", methods=['POST'])
def webhook(config_id):
    config = GirConfig.Get(config_id)
    if config is None:
        return 'Invalid config_id: "%s".' % config_id
    handler = Handler(config)
    return handler()


@app.route("/message", methods=['POST'])
def message():
    config = dict(
        message = '`message`',
        icon_url = 'gir_sitting.png',
        username = '`user`@esss.com.br',
    )
    handler = Handler(config)
    return handler()


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
