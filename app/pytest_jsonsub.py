from __future__ import unicode_literals
import pytest



def test_JsonSub():
    from jsonsub import JsonSub

    data = {
        'message' : 'Hello, world!',
        'build' : {
            'id' : 388,
            'state' : 'success',
        },
    }
    assert JsonSub('`message`', data) == 'Hello, world!'
    assert JsonSub('Build id `build.id` is `build.state`.', data) == 'Build id 388 is success.'

    with pytest.raises(AssertionError):
        JsonSub('`message`', '{"message": "error"')


def test_Remapping():
    from jsonsub import Remapping

    data = {
        'message' : 'Hello, world!',
        'build' : {
            'id' : 388,
            'state' : 'success',
        },
    }
    assert Remapping(
        {
            '__key' : '`build.state`',
            '__default' : 'Unknown',
            'success' : ':yes:',
            'failed' : ':no:',
        },
        data
    ) == ':yes:'

    data['build']['state'] = 'failed'
    assert Remapping(
        {
            '__key' : '`build.state`',
            '__default' : 'Unknown',
            'success' : ':yes:',
            'failed' : ':no:',
        },
        data
    ) == ':no:'

    data['build']['state'] = 'error'
    assert Remapping(
        {
            '__key' : '`build.state`',
            '__default' : 'Unknown',
            'success' : ':yes:',
            'failed' : ':no:',
        },
        data
    ) == 'Unknown'

    # Tests missing __key error
    with pytest.raises(AssertionError):
        Remapping(
            {
                '__default' : 'Unknown',
                'success' : ':yes:',
                'failed' : ':no:',
            },
            data
        )

    # Tests missing __default error
    with pytest.raises(AssertionError):
        Remapping(
            {
                '__key' : '`build.state`',
                'success' : ':yes:',
                'failed' : ':no:',
            },
            data
        )
