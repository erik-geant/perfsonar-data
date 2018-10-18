# esmond_helper

- Python module for exposing simplified views of perfSONAR
  data extracted from esmond archives
- provides an http server for querying data

## requirements

- Python 3
- TODO ...

## running

1. install the package (in a ``virtualenv`` would be nice, of course)

2. create a new database, if necessary

    ```bash
      FLASK_APP=esmond_helper flask db upgrade
    ```

3. run the app

    ```bash
    export FLASK_APP=esmond_helper flask run
    ```

   or ...

    ```bash
    python -m esmond_helper.app
    ```

   or ...

    ```bash
    gunicorn "esmond_helper:create_app()" -b 0.0.0.0:5555
    ```

4. unit tests

    ```bash
    pip install -r requirements.txt
    # cd somewhere the test runner will find the tests in the ``tests`` directory
    py.test
    # or ...
    py.test --cov-report html:coverage --cov-report term --cov perfsonar_data
    ```


## notes


* TODO

  - runtime options, either cli or some config file
     - db is currently hard-coded to ``/tmp/esmond-helper.sqlite``
     - server port is currently hard-coded to ``8234``
  - proxy needs to expire documents (add ``expiration`` col to ``docs`` table)


## protocol

### general

Request must use the POST method and must contain at least the following headers:

```http
Accept: application/json
Content-type: application/json
```
  
### resource: /slshosts

All the hosts

Request payload is optional, but if present must be of the form:

```json
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "url": {"type": "string"}
    },
    "required": ["url", "id"]
}
```

Responses are json, the following is an example:

```json
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
```

### resource: /esmond/participants

All the tests running on a particular host

Request payload must be of the form:

```json
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
     "properties": {
    "url": {"type": "string"}
    },
    "required": ["url", "id"]
}
```

Responses are json, the following is an example:

```json
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
```

### resource: /esmond/series

Timeseries of a particular test

Request payload should be of the form:

```json
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
```

Responses are json, the following is an example:

 ```json
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
```

### resource: /grafana/version

This resource accepts both GET and POST requests,
and ignores any payload.

The response is a string containing the protocol version
supported by the server.

### resource: /grafana/metrics

Use this resource to request a list of metrics available
as time series.  The returned list is intended to be used
in the grafana query editor.

Note that the current module is a proof-of-concept, and
measurement types are limited to those with simple
single-value timeseries.  (After further discussion we'll
have a better idea how far to go in representing and
navigating an esmond archive.)

Requests must be formatted according to the following schema:

```json
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "eventtypes": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "throughput",
                        "packet-count-sent",
                        "packet-count-lost"]
                }
            },
            "cacheseconds": {
                "type": "integer",
                "minimum": 0,
                "exclusiveMinimum": True
            }
        },
        "required": ["hostname"]
    }
```


Responses will be formatted according to the following schema:

```json
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "value": {"type": "string"}
            },
            "require": ["text", "value"],
            "additionalProperties": False
    }
```

### resource: /grafana/timeseries

Use this resource to request the list of timeseries
datapoints for a particular metric.

Requests must be formatted according to the following schema.
The value of `tsurl` should be the
value of one of the `value` elements from the
`/grafana/metrics` response.

```json
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "tsurl": {"type": "string"}
        },
        "required": ["hostname", "tsurl"]
    }
```

Responses will be formatted according to the following schema:

```json
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {
            "type": "array",
            "items": [
                {"type": "number"},
                {"type": "number"}
            ]
        }
    }
```
