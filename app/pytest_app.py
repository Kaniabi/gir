from __future__ import unicode_literals
from app import app
from xml_factory import XmlFactory
import mock



@mock.patch('worker.Slack.Message')
def test_message(mock_message):
    tester = app.test_client()
    data = XmlFactory('')
    data['message'] = 'alpha'
    data['user'] = 'bravo'
    data['host'] = 'charlie'
    data['room'] = 'delta'
    response = tester.post('/message', data=data.AsJson())
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'alpha',
        'http://static.tumblr.com/2qdysyt/AaTm73sce/gir_sitting.png',
        'bravo@charlie'
    )


@mock.patch('worker.Slack.Message')
def test_jira(mock_message):
    tester = app.test_client()
    data = XmlFactory('')
    data['issue/key'] = 'alpha'
    data['issue/self'] = 'bravo'
    data['issue/fields/summary'] = 'charlie'
    data['user/name'] = 'delta'
    response = tester.post('/jira', data=data.AsJson())
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        '<bravo|alpha>: charlie [@delta]',
        'https://developer.atlassian.com/imgs/jira.png',
        'Jira',
    )


@mock.patch('worker.Slack.Message')
def test_stash(mock_message):
    tester = app.test_client()
    data = XmlFactory('')
    data['repository/slug'] = 'alpha'
    response = tester.post('/stash', data=data.AsJson())
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    mock_message.assert_called_once_with(
        'Commit on alpha',
        'https://developer.atlassian.com/imgs/stash.png',
        'Stash',
    )


def test_jenkins():
    tester = app.test_client()
    data = XmlFactory('')
    data['url'] = 'alpha'
    data['name'] = 'bravo'
    data['build/full_url'] = 'charlie'
    data['build/number'] = '999'
    data['build/phase'] = 'FINALIZED'
    data['build/status'] = 'SUCCESS'
    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/jenkins', data=data.AsJson())
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :white_check_mark: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
            'Jenkins',
        )

    data['build/status'] = 'FAILURE'
    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/jenkins', data=data.AsJson())
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :no_entry: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
            'Jenkins',
        )

    data['build/status'] = 'ABORTED'
    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/jenkins', data=data.AsJson())
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :warning: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
            'Jenkins',
        )

    data['build/status'] = 'UNSTABLE'
    with mock.patch('worker.Slack.Message') as mock_message:
        response = tester.post('/jenkins', data=data.AsJson())
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        mock_message.assert_called_once_with(
            'Job :warning: <https://eden.esss.com.br/jenkins/alpha|bravo> <charlie|#999>.',
            'https://slack.global.ssl.fastly.net/20653/img/services/jenkins-ci_48.png',
            'Jenkins',
        )
