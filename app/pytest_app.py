from __future__ import unicode_literals
from app import app
from datatree import Tree
import mock


@mock.patch('worker.Slack.Message')
def test_message(mock_message):
    data = Tree()
    data.message('alpha')
    data.user('bravo')
    data.host('charlie')
    data.room('delta')
    data = data.render('json')

    tester = app.test_client()
    response = tester.post('/message', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'alpha',
        'http://static.tumblr.com/2qdysyt/AaTm73sce/gir_sitting.png',
        'bravo@charlie'
    )


@mock.patch('worker.Slack.Message')
def test_jira(mock_message):
    data = Tree()
    with data.issue() as issue:
        issue.key('alpha')
        issue.self('bravo')
        with issue.fields() as fields:
            fields.summary('charlie')
    with data.user() as user:
        user.name('delta')
    data = data.render('json')

    tester = app.test_client()
    response = tester.post('/jira', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        '<bravo|alpha>: charlie [@delta]',
        'https://developer.atlassian.com/imgs/jira.png',
        'Jira',
    )


@mock.patch('worker.Slack.Message')
def test_stash(mock_message):
    data = Tree()
    data.repository().slug('alpha')
    data = data.render('json')

    tester = app.test_client()
    response = tester.post('/stash', data=data, headers={'Content-type': 'application/json'})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'Commit on alpha',
        'https://developer.atlassian.com/imgs/stash.png',
        'Stash',
    )


def test_jenkins():

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
        response = tester.post('/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :white_check_mark: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
            'Jenkins',
        )

    post_data = CreatePostData(status='FAILURE')

    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :no_entry: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
            'Jenkins',
        )

    post_data = CreatePostData(status='ABORTED')

    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :warning: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
            'Jenkins',
        )

    post_data = CreatePostData(status='UNSTABLE')

    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/jenkins', data=post_data, headers={'Content-type': 'application/json'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :warning: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
            'Jenkins',
        )
