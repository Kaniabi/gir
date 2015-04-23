from __future__ import unicode_literals
from flask import Flask, request, render_template
from worker import Slack



def CreateApp(configfile=None):
    from flask.ext.appconfig import AppConfig
    from rq_dashboard import RQDashboard
    from flask_debug import Debug

    result = Flask(__name__)
    result.debug = True
    AppConfig(result, default_settings="default_config", configfile=configfile)
    RQDashboard(result)
    Debug(result)
    return result


app = CreateApp()

Slack.SLACK_TOKEN = app.config['SLACK_TOKEN']
Slack.SLACK_USER = app.config['SLACK_USER']
Slack.SLACK_HOST = app.config['SLACK_HOST']
Slack.REDIS_HOST = app.config['REDIS_HOST']
Slack.REDIS_PORT = app.config['REDIS_PORT']
Slack.REDIS_DB = app.config['REDIS_DB']
Slack.REDIS_PASSWORD = app.config['REDIS_PASSWORD']
Slack.STATIC_URL = app.config['STATIC_URL']

slack = Slack()

class GirConfig(object):
    '''
    Provides gir webhook configurations to the application.
    '''

    CONFIG = {
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
        server = app.config['COUCHDB_SERVER'],
        database = app.config['COUCHDB_DATABASE']
    ):
        if server is None:
            return None

        from couchdb.client import Server
        couchdb_server = Server(server)
        return couchdb_server[database]


    @classmethod
    def Get(cls, config_id):
        database = cls.GetDatabase()

        if database is not None:
            return database.get(config_id)

        # Fallback from default/local configuration (for now).
        # This is expected for testing.
        return cls.GetLocally(config_id)


    @classmethod
    def GetLocally(cls, config_id):
        return cls.CONFIG.get(config_id)



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

        data = request.get_json()

        # Create new values on data based on remapping dictionary.
        # Check Remapping function for more details.
        # Example:
        #   We use a different emoji depending on the combination of a build (jenkins) phase and status.
        for i_key, i_mapping in remapping.items():
            data[i_key] = Remapping(i_mapping, data)

        # Exits without sending the message to Slack under some conditions (early_exit).
        for i_expression, i_description, i_result in early_exit:
            i_expression = JsonSub(i_expression, data)
            if eval(i_expression):
                return i_result

        # Sends the message (using queue)
        message = JsonSub(message, data)
        username = JsonSub(username, data)
        icon_url = Slack.StaticResource(icon_url)
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
    return render_template(
        'index.html',
        GIR_STATIC_URL=app.config['STATIC_URL'],
    )


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
        username = '`username`',
    )
    handler = Handler(config)
    return handler()


if __name__ == "__main__":
    port = int(app.config['FLASK_PORT'])
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
