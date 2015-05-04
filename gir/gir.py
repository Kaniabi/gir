from __future__ import unicode_literals
from flask.ext.rq import job
import json
import os


def CreateApp(configfile=None):
    from flask import Flask
    from flask.ext.appconfig import AppConfig
    from rq_dashboard import RQDashboard
    from flask_debug import Debug
    from flask.ext.rq import RQ

    result = Flask(__name__)
    AppConfig(result, default_settings="default_config", configfile=configfile)
    result.config['RQ_DEFAULT_URL'] = result.config['REDIS_URL']
    RQDashboard(result)
    Debug(result)
    RQ(result)
    return result


app = CreateApp()


def GetConfig(config):
    '''
    Obtain the flask application configuration with a twist: expand any environment variables.

    :param unicode config:
    :return unicode:
    '''
    import six

    result = app.config[config]
    if isinstance(result, six.text_type):
        result = os.path.expandvars(result)
    return result


@app.route("/")
def index():
    from flask import render_template
    return render_template(
        'index.html',
        GIR_STATIC_URL=GetConfig('STATIC_URL'),
    )


@app.route("/message", methods=['GET', 'POST'])
def message():
    from flask import request

    if request.method == 'GET':
        result = '<pre>curl -X POST -r {"message" : "Oi"}</pre>'
    else:
        result = EventFlow.HandleRoute(
            request.get_json(),
            '`message`',
            icon_url='gir_sitting.png',
            username='`username`',
        )
    return result


@app.route("/webhook/<event_id>", methods=('GET', 'POST'))
def webhook(event_id):
    from flask import request, render_template

    if request.method == 'GET':
        # Print some information
        routes = EventFlow.GetRoutes(event_id)
        if routes:
            pretty_routes = []
            for i_route in routes:
                pretty_routes.append(
                    json.dumps(i_route, sort_keys=True, indent=2, separators=(',',':'))
                )
            result = render_template(
                'routes.html',
                event_id=event_id,
                routes=pretty_routes,
            )
        else:
            routes = EventFlow.ListRoutes()
            result = render_template(
                'no_route.html',
                event_id=event_id,
                routes=routes,
            )

        return result
    else:
        # Handle JSON payload.
        for i_route in EventFlow.GetRoutes(event_id):
            if i_route is None:
                return (
                    'Invalid event_id: "%s".' % event_id,
                    400,
                    {
                        'payload' : request.data
                    }
                )
            return EventFlow.HandleRoute(
                request.get_json(),
                i_route['message'],
                icon_url=i_route['icon_url'],
                username=i_route['username'],
                remapping=i_route.get('remapping', {}),
                early_exit=i_route.get('early_exit', {}),
            )


class EventFlow(object):
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
                {
                    'expression' : '"`build.phase`" == "COMPLETED"',
                    'description' : 'Ignore COMPLETED events in favor of FINALIZED (after all post-build).',
                    'result' : 'OK',
                },
            ],
        ),
    }

    @classmethod
    def GetDatabase(
        cls,
        server = GetConfig('COUCHDB_SERVER'),
        database = GetConfig('COUCHDB_DATABASE')
    ):
        if server is None:
            return None

        from couchdb.client import Server
        couchdb_server = Server(server)

        return couchdb_server[database]


    @classmethod
    def GetRoutes(cls, config_id):
        '''
        :param unicode config_id:
        :return list(dict):
        '''
        database = cls.GetDatabase()

        if database is not None:
            result = database.get(config_id)
            if result is None:
                return []
            else:
                return [result]

        # Fallback from default/local configuration (for now).
        # This is expected for testing.
        return cls.GetLocally(config_id)


    @classmethod
    def ListRoutes(cls):
        database = cls.GetDatabase()
        if database is not None:
            map_func = "function(doc) { emit(doc.name, 1); }"
            return [i.id for i in database.query(map_func)]
        else:
            return sorted(cls.CONFIGS.keys())


    @classmethod
    def GetLocally(cls, config_id):
        return [cls.CONFIG.get(config_id)]


    @classmethod
    def HandleRoute(cls, data, message, icon_url, username, remapping={}, early_exit={}):
        from jsonsub import JsonSub, Remapping

        # Create new values on data based on remapping dictionary.
        # Check Remapping function for more details.
        # Example:
        #   We use a different emoji depending on the combination of a build (jenkins) phase and status.
        for i_key, i_mapping in remapping.items():
            data[i_key] = Remapping(i_mapping, data)

        # Exits without sending the message to Slack under some conditions (early_exit).
        for i_early_exit in early_exit:
            expression = i_early_exit['expression']
            result = i_early_exit['result']
            expression = JsonSub(expression, data)
            if eval(expression):
                return result

        # Sends the message (using queue)
        message = JsonSub(message, data)
        username = JsonSub(username, data)
        icon_url = GetConfig('STATIC_URL') + icon_url
        icon_url = GravatarUrl(username, default=icon_url)
        SlackMessage.delay(message, icon_url, username)

        return 'OK'


def GravatarUrl(email, size=42, default=None):
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


@job('normal')
def SlackMessage(message, icon_url=None, username=None, room=None):
    from slackclient import SlackClient

    slack_token = GetConfig('SLACK_TOKEN')
    assert slack_token is not None, 'Please configure SLACK_TOKEN flask configuration.'

    icon_url = icon_url or GetConfig('STATIC_URL') + 'gir_stare.png'
    username = username or GetConfig('SLACK_USER') + '@' + GetConfig('SLACK_HOST')

    room = room or GetConfig('SLACK_ROOM')

    slack = SlackClient(slack_token)
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
    port = int(GetConfig('FLASK_PORT'))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
