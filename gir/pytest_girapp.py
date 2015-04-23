from __future__ import unicode_literals
import json
from girapp import app, GirConfig
from datatree import Tree
import mock



@mock.patch('worker.Slack.Message')
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
        'http://www.gravatar.com/avatar/3a1d8ffc9b5c06a8f1f4752aa8b5f59f?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fgir_sitting.png&s=42',
        'bravo@esss.com.br'
    )


@mock.patch('worker.Slack.Message')
@mock.patch('girapp.GirConfig.Get', new=GirConfig.GetLocally)
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
        'http://www.gravatar.com/avatar/3a1d8ffc9b5c06a8f1f4752aa8b5f59f?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fjira.png&s=42',
        'bravo@esss.com.br',
    )


@mock.patch('worker.Slack.Message')
@mock.patch('girapp.GirConfig.Get', new=GirConfig.GetLocally)
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
                "emailAddress": "ama@esss.com.br"
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
        'http://www.gravatar.com/avatar/49d2560e31d46da8237b9a32852ce080?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fstash.png&s=42',
        'ama@esss.com.br',
    )


@mock.patch('girapp.GirConfig.Get', new=GirConfig.GetLocally)
def test_webhook_jenkins():

    def CreatePostData(phase='FINALIZED', status='SUCCESS'):
        data = Tree()
        data.url('alpha')
        data.name('bravo')
        with data.build() as build:
            build.full_url('charlie')
            build.number('999')
            build.phase(phase)
            build.status(status)
        return data.render('json')

    post_data = CreatePostData()

    tester = app.test_client()
    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/webhook/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :white_check_mark: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'http://www.gravatar.com/avatar/ab63a76362c3972ac83d5cb8830fdb51?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fjenkins.png&s=42',
            'Jenkins',
        )

    post_data = CreatePostData(status='FAILURE')

    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/webhook/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :no_entry: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'http://www.gravatar.com/avatar/ab63a76362c3972ac83d5cb8830fdb51?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fjenkins.png&s=42',
            'Jenkins',
        )

    post_data = CreatePostData(status='ABORTED')

    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/webhook/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :warning: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'http://www.gravatar.com/avatar/ab63a76362c3972ac83d5cb8830fdb51?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fjenkins.png&s=42',
            'Jenkins',
        )

    post_data = CreatePostData(status='UNSTABLE')

    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/webhook/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :warning: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'http://www.gravatar.com/avatar/ab63a76362c3972ac83d5cb8830fdb51?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fjenkins.png&s=42',
            'Jenkins',
        )


@mock.patch('worker.Slack.Message')
@mock.patch('girapp.GirConfig.Get', new=GirConfig.GetLocally)
def test_webhook_github(mock_message):
    data = {
        'repository' : {
            'url' : 'http://github.com/kaniabi/gir',
            'name' : 'gir',
            'full_name' : 'kaniabi/gir',
        },
        'pusher' : {
            'email' : 'kaniabi@gmail.com',
        },
    }
    data = json.dumps(data)

    tester = app.test_client()
    response = tester.post('/webhook/github', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'Commit on <http://github.com/kaniabi/gir|kaniabi/gir>',
        'http://www.gravatar.com/avatar/8101da6577a821fb6f95098de8f1a293?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fgithub.png&s=42',
        'kaniabi@gmail.com',
    )


@mock.patch('worker.Slack.Message')
@mock.patch('girapp.GirConfig.Get', new=GirConfig.GetLocally)
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
        'http://www.gravatar.com/avatar/afbc9a4d12e9481a8b1e68912685c436?d=http%3A%2F%2F188.226.245.90%2Fstatic%2Fcircle.png&s=42',
        'CircleCI',
    )


@mock.patch('girapp.GirConfig.Get', new=GirConfig.GetLocally)
def test_webhook_error():
    data = {}
    data = json.dumps(data)

    tester = app.test_client()
    response = tester.post('/webhook/error', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.data == b'Invalid config_id: "error".'
