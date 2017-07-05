from perfsonar_data import proxy

_ESMOND_ARCHIVE_PATH = "esmond/perfsonar/archive/"


def load_tests(ps_base_url, session):
    """
    loads the esmond test archive summary
    :param ps_base_url: perfSONAR base url
    :param session: a sqlalchemy session instance
    :return: list of test structs
    """
    archive = proxy.load_url_json(ps_base_url + _ESMOND_ARCHIVE_PATH, session)
    assert isinstance(archive, (list, tuple))
    return archive


def get_test_participants(list_of_tests):
    """
    returns a list of unique participants, each of which
    is a dict with format:
        {"source": <address>, "destination": <address>}

    :param list_of_tests: list of elements from a perfsonar archive summary
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

    :param list_of_tests: list of elements from a perfsonar archive summary
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

    :param list_of_tests: list of elements from a perfsonar archive summary
    :return: dict with items (tool name, list of tests)
    """
    result = {}
    for t in list_of_tests:
        tool_name = t["tool-name"]
        if tool_name not in result:
            result[tool_name] = []
        result[tool_name].append(t)
    return result


def get_time_series(esmond_base_url, summary_id, session):
    data = proxy.load_url_json(
        esmond_base_url + _ESMOND_ARCHIVE_PATH + summary_id, session)
    assert isinstance(data, (list, tuple))
    return data
