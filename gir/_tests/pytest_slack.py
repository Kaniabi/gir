from __future__ import unicode_literals
from slackapp import app
import json
import mock



@mock.patch('slackapp.SlackMessage')
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
        'gir_sitting.png',
        'bravo@esss.com.br'
    )
