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


def test_StashJson():
    from jsonsub import JsonSub

    data = {
      "repository": {
        "slug": "ben10",
        "id": 835,
        "name": "ben10",
        "scmId": "git",
        "state": "AVAILABLE",
        "statusMessage": "Available",
        "forkable": True,
        "project": {
          "key": "ESSS",
          "id": 1,
          "name": "ESSS",
          "description": "Dev projects",
          "public": False,
          "type": "NORMAL"
        },
        "public": False
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
        "size": 1,
        "limit": 100,
        "isLastPage": True,
        "values": [
          {
            "fromCommit": {
              "id": "0b0eb27fdc65272250da919e4d420e021ec28b5a",
              "displayId": "0b0eb27fdc6"
            },
            "toCommit": {
              "id": "8ad4928929b929e35e2a261eb672bd657214c452",
              "displayId": "8ad4928929b",
              "author": {
                "name": "Alexandre Andrade",
                "emailAddress": "ama@esss.com.br"
              },
              "authorTimestamp": 1429547664000,
              "message": "Adding XmlFactory.AsDict and XmlFactory.AsJson.",
              "parents": [
                {
                  "id": "0b0eb27fdc65272250da919e4d420e021ec28b5a",
                  "displayId": "0b0eb27fdc6"
                }
              ]
            },
            "changes": {
              "size": 2,
              "limit": 100,
              "isLastPage": True,
              "values": [
                {
                  "contentId": "9efca57c0270f02dfdf4e9e5ee20d724eb05b3d0",
                  "path": {
                    "components": [
                      "source",
                      "python",
                      "xml_factory",
                      "_tests",
                      "pytest_xml_factory.py"
                    ],
                    "parent": "source/python/xml_factory/_tests",
                    "name": "pytest_xml_factory.py",
                    "extension": "py",
                    "toString": "source/python/xml_factory/_tests/pytest_xml_factory.py"
                  },
                  "executable": False,
                  "percentUnchanged": -1,
                  "type": "MODIFY",
                  "nodeType": "FILE",
                  "srcExecutable": False,
                  "link": {
                    "url": "/projects/ESSS/repos/ben10/commits/8ad4928929b929e35e2a261eb672bd657214c452#source/python/xml_factory/_tests/pytest_xml_factory.py",
                    "rel": "self"
                  },
                  "links": {
                    "self": [
                      {
                        "href": "https://eden.esss.com.br/stash/projects/ESSS/repos/ben10/commits/8ad4928929b929e35e2a261eb672bd657214c452#source/python/xml_factory/_tests/pytest_xml_factory.py"
                      }
                    ]
                  }
                },
                {
                  "contentId": "ca1e1f2648ac8ceacf13838c4be8b0767904d8b5",
                  "path": {
                    "components": [
                      "source",
                      "python",
                      "xml_factory",
                      "_xml_factory.py"
                    ],
                    "parent": "source/python/xml_factory",
                    "name": "_xml_factory.py",
                    "extension": "py",
                    "toString": "source/python/xml_factory/_xml_factory.py"
                  },
                  "executable": False,
                  "percentUnchanged": -1,
                  "type": "MODIFY",
                  "nodeType": "FILE",
                  "srcExecutable": False,
                  "link": {
                    "url": "/projects/ESSS/repos/ben10/commits/8ad4928929b929e35e2a261eb672bd657214c452#source/python/xml_factory/_xml_factory.py",
                    "rel": "self"
                  },
                  "links": {
                    "self": [
                      {
                        "href": "https://eden.esss.com.br/stash/projects/ESSS/repos/ben10/commits/8ad4928929b929e35e2a261eb672bd657214c452#source/python/xml_factory/_xml_factory.py"
                      }
                    ]
                  }
                }
              ],
              "start": 0
            },
            "link": {
              "url": "/projects/ESSS/repos/ben10/commits/8ad4928929b929e35e2a261eb672bd657214c452#source/python/xml_factory/_xml_factory.py",
              "rel": "self"
            },
            "links": {
              "self": [
                {
                  "href": "https://eden.esss.com.br/stash/projects/ESSS/repos/ben10/commits/8ad4928929b929e35e2a261eb672bd657214c452#source/python/xml_factory/_xml_factory.py"
                }
              ]
            }
          }
        ],
        "start": 0
      }
    }

    assert JsonSub('`refChanges[0].refId`', data) == 'refs/heads/ama'
    assert JsonSub('`changesets.values[0].toCommit.author.emailAddress`', data) == 'ama@esss.com.br'
    assert JsonSub('`changesets.values[0].toCommit.message`', data) == 'Adding XmlFactory.AsDict and XmlFactory.AsJson.'
