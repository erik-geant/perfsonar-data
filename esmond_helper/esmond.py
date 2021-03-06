import time
from esmond_helper import proxy

_ESMOND_ARCHIVE_PATH = "/esmond/perfsonar/archive/"


def _proxy_expires():
    """
    simplification: this module computes uses 120 minutes as
                the proxy expiration time of all requests

    :return: ts 7200 seconds from now
    """
    return 7200 + int(time.time())


def _event_type_nodes(data, measurement_type, metadata_key):
    """
    yields a list of event-type nodes from data tree
    which also have available summaries

    :param data:
    :param measurement_type:
    :param metadata_key:
    :return:
    """
    for participant_pair in data:
        if participant_pair.get("metadata-key", None) == metadata_key:
            for et in participant_pair.get("event-types", []):
                summaries = et.get("summaries", [])
                event_type = et.get("event-type", None)
                if summaries and event_type == measurement_type:
                    yield et


def load_tests(ps_base_url, connection):
    """
    loads the esmond test archive summary
    :param ps_base_url: perfSONAR base url
    :param connection: a db connection
    :return: list of test structs
    """
    archive = proxy.load_url_json(
        ps_base_url.strip("/") + _ESMOND_ARCHIVE_PATH,
        connection,
        expires=_proxy_expires())
    assert isinstance(archive, (list, tuple))
    return archive


def get_test_participants(list_of_tests):
    """
    returns a list of unique participants, each of which
    is a dict with format:
        {"source": <address>, "destination": <address>}

    :param list_of_tests: list of elements from an archive summary
    :return: list of unique participant dicts
    """
    list_of_participants = [{
        "source": t["source"],
        "destination": t["destination"]
        } for t in list_of_tests]
    # frozenset(dict.items) returns a hashable representation of the dict
    partset = {frozenset(p.items()) for p in list_of_participants}
    return [dict(p) for p in partset]


def group_by_participants(list_of_tests):
    """
    list of dicts, each element of which has elements:
        "participants": {"source": <address>, "destination": <address>}
        "tests": list of test elements with the same participants

    :param list_of_tests: list of elements from an archive summary
    :return: list of tests, grouped by participant
    """
    result = {}
    for p in get_test_participants(list_of_tests):
        # frozenset(dict.items) returns a hashable
        # representation of the dict
        result[frozenset(p.items())] = {
            "participants": p,
            "tests": [],
        }

    for t in list_of_tests:
        part = {"source": t["source"], "destination": t["destination"]}
        key = frozenset(part.items())
        result[key]["tests"].append(t)

    return result.values()


def group_by_tool(list_of_tests):
    """
    returns a dict that groups tests by "tool-name", keys
    are tool-name and values are the corresponding test dicts

    :param list_of_tests: list of elements from an archive summary
    :return: dict with items (tool name, list of tests)
    """
    result = {}
    for t in list_of_tests:
        tool_name = t["tool-name"]
        if tool_name not in result:
            result[tool_name] = []
        result[tool_name].append(t)
    return result


def get_time_series(esmond_base_url, summary_id, connection):
    """
    TODO: think of a nice way to use the actual timestamp
          for this series from the archive ... maybe update
          the proxy timestamp based on the returned data

    :param esmond_base_url:
    :param summary_id:
    :param connection: a db connection
    :return:
    """
    data = proxy.load_url_json(
        esmond_base_url.strip("/") + _ESMOND_ARCHIVE_PATH + summary_id,
        connection,
        expires=_proxy_expires())
    assert isinstance(data, (list, tuple))
    return data


def _esmond_base_url(hostname):
    return "http://%s/%s" % (
        hostname.strip("/"), _ESMOND_ARCHIVE_PATH)


def get_available_measurement_types(mp_hostname, connection):
    def _event_types(d):
        for participant_pair in d:
            for et in participant_pair["event-types"]:
                if et["summaries"]:
                    yield et["event-type"]

    data = proxy.load_url_json(
        _esmond_base_url(mp_hostname),
        connection,
        expires=_proxy_expires())
    assert isinstance(data, (list, tuple))

    _et = _event_types(data)
    return list(set(_et))


def get_available_participants(mp_hostname, measurement_type, connection):

    def _participants(d, t):
        for participant_pair in d:
            for et in participant_pair.get("event-types", []):
                summaries = et.get('summaries', [])
                event_type = et.get('event-type', None)
                if summaries and event_type == t:
                    yield {
                        "source":
                            participant_pair.get("source", None),
                        "destination":
                            participant_pair.get("destination", None),
                        "metadata-key":
                            participant_pair.get("metadata-key", None),
                        "time-updated": et["time-updated"]
                            if et.get('time-updated', 0) else 0
                    }

    data = proxy.load_url_json(
        _esmond_base_url(mp_hostname),
        connection,
        expires=_proxy_expires())
    assert isinstance(data, (list, tuple))

    participants = list(_participants(data, measurement_type))
    return sorted(
        participants,
        key=lambda k: k['time-updated'],
        reverse=True)


def get_available_summaries(
        mp_hostname,
        measurement_type,
        metadata_key,
        connection):

    def _summaries(d, t, k):
        for et in _event_type_nodes(d, t, k):
            for s in et['summaries']:
                yield {
                    "type": s["summary-type"],
                    "window": s["summary-window"],
                    "uri": s["uri"]
                }
            yield {
                "type": "base",
                "window": "-",
                "uri": et['base-uri']
            }

    data = proxy.load_url_json(
        _esmond_base_url(mp_hostname),
        connection,
        expires=_proxy_expires())
    assert isinstance(data, (list, tuple))
    return list(_summaries(data, measurement_type, metadata_key))
