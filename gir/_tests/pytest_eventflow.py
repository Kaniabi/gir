from __future__ import unicode_literals
from gir.eventflow import app, EventFlow
import json
import mock



def _GravatarUrl(filename, email='bravo@esss.com.br'):
    import hashlib
    server_ip = 'localhost%3A5000'
    md5 = hashlib.md5(email.encode('ascii').lower()).hexdigest()
    return 'http://www.gravatar.com/avatar/' + md5 + '?d=http%3A%2F%2F' + server_ip + '%2Fstatic%2F' + filename + '&s=42'



@mock.patch('gir.SlackMessage.delay')
def test_message(mock_message):
    data = {
        'message' : 'alpha',
        'username' : 'bravo@esss.com.br',
        'room' : 'delta',
    }
    data = json.dumps(data)

    tester = app.test_client()
    response = tester.post('/message', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'alpha',
        _GravatarUrl('gir_sitting.png'),
        'bravo@esss.com.br'
    )


@mock.patch('gir.SlackMessage.delay')
@mock.patch('gir.EventFlow.GetRoutes', new=EventFlow.GetLocally)
def test_webhook_jira(mock_message):
    data = {
        'issue' : {
            'key' : 'alpha',
            'self' : 'bravo',
            'fields' : {
                'summary' : 'charlie',
            }
        },
        'user' : {
            'name' : 'bravo',
        }
    }
    data = json.dumps(data)

    tester = app.test_client()
    response = tester.post('/webhook/jira', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        '<bravo|alpha>: charlie',
        _GravatarUrl('jira.png'),
        'bravo@esss.com.br',
    )


@mock.patch('gir.SlackMessage.delay')
@mock.patch('gir.EventFlow.GetRoutes', new=EventFlow.GetLocally)
def test_webhook_stash(mock_message):
    data = {
      "repository": {
        "slug": "ben10",
        "project": {
          "key": "ESSS",
          "id": 1,
          "name": "ESSS",
          "description": "Dev projects",
          "public": False,
          "type": "NORMAL"
        },
      },
      "refChanges": [
        {
          "refId": "refs/heads/ama",
          "fromHash": "0b0eb27fdc65272250da919e4d420e021ec28b5a",
          "toHash": "8ad4928929b929e35e2a261eb672bd657214c452",
          "type": "UPDATE"
        }
      ],
      "changesets": {
        "values": [
          {
            "toCommit": {
              "id": "8ad4928929b929e35e2a261eb672bd657214c452",
              "displayId": "8ad4928929b",
              "author": {
                "name": "Alexandre Andrade",
                "emailAddress": "bravo@esss.com.br"
              },
              "message": "Adding XmlFactory.AsDict and XmlFactory.AsJson.",
            },
          }
        ]
      }
    }
    data = json.dumps(data)

    tester = app.test_client()
    response = tester.post('/webhook/stash', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'ben10#refs/heads/ama: 8ad4928929b: Adding XmlFactory.AsDict and XmlFactory.AsJson.',
        _GravatarUrl('stash.png'),
        'bravo@esss.com.br',
    )


@mock.patch('gir.EventFlow.GetRoutes', new=EventFlow.GetLocally)
def test_webhook_jenkins():

    def CreatePostData(phase='FINALIZED', status='SUCCESS'):
        data = {
            'url' : 'alpha',
            'name' : 'bravo',
            'build' : {
                'full_url' : 'charlie',
                'number' : '999',
                'phase' : phase,
                'status' : status,
            }
        }
        return json.dumps(data)

    post_data = CreatePostData()

    tester = app.test_client()
    with mock.patch('gir.SlackMessage.delay') as mock_message:
        response = tester.post('/webhook/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :white_check_mark: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            _GravatarUrl('jenkins.png', 'Jenkins'),
            'Jenkins',
        )

    post_data = CreatePostData(status='FAILURE')

    with mock.patch('gir.SlackMessage.delay') as mock_message:
        response = tester.post('/webhook/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :no_entry: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            _GravatarUrl('jenkins.png', 'Jenkins'),
            'Jenkins',
        )

    post_data = CreatePostData(status='ABORTED')

    with mock.patch('gir.SlackMessage.delay') as mock_message:
        response = tester.post('/webhook/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :warning: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            _GravatarUrl('jenkins.png', 'Jenkins'),
            'Jenkins',
        )

    post_data = CreatePostData(status='UNSTABLE')

    with mock.patch('gir.SlackMessage.delay') as mock_message:
        response = tester.post('/webhook/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :warning: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            _GravatarUrl('jenkins.png', 'Jenkins'),
            'Jenkins',
        )


@mock.patch('gir.SlackMessage.delay')
@mock.patch('gir.EventFlow.GetRoutes', new=EventFlow.GetLocally)
def test_webhook_github(mock_message):
    data = {
        'repository' : {
            'url' : 'http://github.com/kaniabi/gir',
            'name' : 'gir',
            'full_name' : 'kaniabi/gir',
        },
        'pusher' : {
            'email' : 'bravo@esss.com.br',
        },
    }
    data = json.dumps(data)

    tester = app.test_client()
    response = tester.post('/webhook/github', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'Commit on <http://github.com/kaniabi/gir|kaniabi/gir>',
        _GravatarUrl('github.png'),
        'bravo@esss.com.br',
    )


@mock.patch('gir.SlackMessage.delay')
@mock.patch('gir.EventFlow.GetRoutes', new=EventFlow.GetLocally)
def test_webhook_circleci(mock_message):
    data = {
        'payload' : {
            'build_url' : 'alpha',
            'vcs_url' : 'bravo',
            'branch' : 'charlie',
        },
    }
    data = json.dumps(data)

    tester = app.test_client()
    response = tester.post('/webhook/circleci', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'Job <alpha|bravo#charlie>',
        _GravatarUrl('circle.png', 'CircleCI'),
        'CircleCI',
    )


@mock.patch('gir.EventFlow.GetRoutes', new=EventFlow.GetLocally)
def test_webhook_error():
    data = {}
    data = json.dumps(data)

    tester = app.test_client()
    response = tester.post('/webhook/error', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 400
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.data == b'Invalid event_id: "error".'
