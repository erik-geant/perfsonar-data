
perfsonar_data
==============

- Python module for exposing simplified views of perfSONAR test nodes and test data
- provides an http server for querying data

requirements
============

- Python 3
- TODO ...

running
=======

1. install the package (in a ``virtualenv`` would be nice, of course)

2. create a new database, if necessary

.. code:: bash

  FLASK_APP=perfsonar_data.app flask db upgrade
  
3. run the app

.. code:: bash

  python perfsonar_data/app
  
4. unit tests

.. code:: bash

  pip install -r requirements.txt
  # cd somewhere the test runner will find the tests in the ``tests`` directory
  py.test 
  # or ...
  py.test --cov-report html:coverage --cov-report term --cov perfsonar_data


notes
-----

* TODO

  - runtime options, either cli or some config file
     - db is currently hard-coded to ``/tmp/perfsonar-data.sqlite``
     - server port is currently hard-coded to ``8234``
  - proxy needs to expire documents (add ``expiration`` col to ``docs`` table)


protocol
========

general
-------

Request must use the POST method and must contain at least the following headers:

.. code:: http

  Accept: application/json
  Content-type: application/json
  
  
resource: /slshosts
-------------------

Request payload is optional, but if present must be of the form:

.. code:: json

  {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "url": {"type": "string"}
    },
    "required": ["url", "id"]
  }

Responses are json, the following is an example:

.. code:: json

  [
    {
        "host-name": [
            "137.164.28.130"
        ],
        "psmetadata-ma-locator": [],
        "location": {
            "city": null,
            "country": null,
            "latitude": null,
            "longitude": null,
            "sitename": null
        }
    },
    {
        "host-name": [
            "202.122.37.82"
        ],
        "psmetadata-ma-locator": [
            "http://202.122.37.82/esmond/perfsonar/archive",
            "https://202.122.37.82/esmond/perfsonar/archive"
        ],
        "location": {
            "city": null,
            "country": null,
            "latitude": null,
            "longitude": null,
            "sitename": null
        }
    },
    {
        "host-name": [
            "198.10.15.23",
            "ps-antl-meter-10g.nren.nasa.gov"
        ],
        "psmetadata-ma-locator": [
            "http://[2001:4d0:108:c016:198:10:15:23]/esmond/perfsonar/archive",
            "http://198.10.15.23/esmond/perfsonar/archive",
            "https://[2001:4d0:108:c016:198:10:15:23]/esmond/perfsonar/archive",
            "https://198.10.15.23/esmond/perfsonar/archive"
        ],
        "location": {
            "city": "Moffett Field",
            "country": "US",
            "latitude": "37.412809",
            "longitude": "-122.063158",
            "sitename": "NASA Ames NREN (LAB)"
        }
    }
  ]

resource: /esmond/participants
------------------------------

Request payload must be of the form:

.. code:: json

  {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "url": {"type": "string"}
    },
    "required": ["url", "id"]
  }

Responses are json, the following is an example:

.. code:: json

  [
    {
        "destination": "62.40.106.177",
        "source": "158.125.250.70",
        "summaries": [
            {
                "ref": "81e49113d33c4d6e8ad0da92e0937b08/histogram-ttl/statistics/0",
                "time": 1472774366,
                "type": "histogram-ttl",
                "window": "0"
            },
            {
                "ref": "81e49113d33c4d6e8ad0da92e0937b08/histogram-owdelay/aggregations/300",
                "time": 1472774365,
                "type": "histogram-owdelay",
                "window": "300"
            }
        ]
    },
    {
        "source": "2001:630:301:b018::616a:b17e",
        "destination": "2001:798:bb:2::8e",
        "summaries": [
            {
                "ref": "17ef50d7d1e74f85be0049206bcaa129/throughput/averages/86400",
                "time": 1499166631,
                "type": "throughput",
                "window": "86400"
            },
            {
                "ref": "875d4b6a550341d4b223ee636488dd46/throughput/averages/86400",
                "time": 1496358530,
                "type": "throughput",
                "window": "86400"
            }
        ]
    }
  ]


resource: /esmond/series
------------------------

Request payload should be of the form:

.. code:: json

  {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "url": {"type": "string"},
        "id": {"type": "string"},
        "keys": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string"}
        }
    },
    "required": ["url", "id"]
  }

Responses are json, the following is an example:

.. code:: json

  {
    "maximum": [
        {
            "ts": 1467593400,
            "value": 24.4
        },
        {
            "ts": 1467593700,
            "value": 26.2
        }
    ],
    "minimum": [
        {
            "ts": 1467593400,
            "value": 24.1
        },
        {
            "ts": 1467593700,
            "value": 24.1
        }
    ]
  }


    
