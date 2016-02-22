##############################################################################
#
# Copyright (c) 2014, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of hubspot-connection
# <https://github.com/2degrees/hubspot-connection>, which is subject to the
# provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
from builtins import str as text
from copy import deepcopy

from pyrecord import Record


APICall = Record.create_type(
    'APICall',
    'url_path',
    'http_method',
    'query_string_args',
    'request_body_deserialization',
    query_string_args=None,
    request_body_deserialization=None,
    )


SuccessfulAPICall = APICall.extend_type(
    'SuccessfulAPICall',
    'response_body_deserialization',
    )


UnsuccessfulAPICall = APICall.extend_type('UnsuccessfulAPICall', 'exception')


class MockPortalConnection(object):
    """
    Mock representation of a
    :class:`~hubspot.connection.PortalConnection`

    """
    def __init__(self, *api_calls_simulators):
        super(MockPortalConnection, self).__init__()

        self._expected_api_calls = []
        for api_calls_simulator in api_calls_simulators:
            for api_call in api_calls_simulator():
                api_call = _normalize_api_call(api_call)
                self._expected_api_calls.append(api_call)

        self._request_count = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            return

        expected_api_call_count = len(self._expected_api_calls)
        pending_api_call_count = expected_api_call_count - self._request_count
        error_message = \
            '{} more requests were expected'.format(pending_api_call_count)
        assert expected_api_call_count == self._request_count, error_message

    def send_get_request(self, url_path, query_string_args=None):
        return self._call_remote_method(url_path, 'GET', query_string_args)

    def send_post_request(self, url_path, body_deserialization):
        return self._call_remote_method(
            url_path,
            'POST',
            request_body_deserialization=body_deserialization,
            )

    def send_put_request(self, url_path, body_deserialization):
        return self._call_remote_method(
            url_path,
            'PUT',
            request_body_deserialization=body_deserialization,
            )

    def send_delete_request(self, url_path):
        return self._call_remote_method(url_path, 'DELETE')

    def _call_remote_method(
        self,
        url_path,
        http_method,
        query_string_args=None,
        request_body_deserialization=None,
        ):
        self._require_enough_api_calls(url_path)

        expected_api_call = self._expected_api_calls[self._request_count]

        _assert_request_matches_api_call(
            expected_api_call,
            url_path,
            http_method,
            query_string_args,
            request_body_deserialization,
            )

        self._request_count += 1

        if isinstance(expected_api_call, UnsuccessfulAPICall):
            raise expected_api_call.exception

        return expected_api_call.response_body_deserialization

    @property
    def api_calls(self):
        api_calls = self._expected_api_calls[:self._request_count]
        return api_calls

    def _require_enough_api_calls(self, url_path):
        are_enough_api_calls = \
            self._request_count < len(self._expected_api_calls)
        error_message = 'Not enough API calls for new requests ' \
            '(requested {!r})'.format(url_path)
        assert are_enough_api_calls, error_message


def _normalize_api_call(api_call):
    if isinstance(api_call, SuccessfulAPICall):
        api_call = deepcopy(api_call)
        api_call.response_body_deserialization = \
            _convert_object_strings_to_unicode(
                api_call.response_body_deserialization,
                )
    return api_call


def _assert_request_matches_api_call(
    api_call,
    url_path,
    http_method,
    query_string_args,
    request_body_deserialization,
    ):
    url_paths_match = api_call.url_path == url_path
    assert url_paths_match, \
        'Expected URL path {!r}, got {!r}'.format(api_call.url_path, url_path)

    query_string_args_match = api_call.query_string_args == query_string_args
    assert query_string_args_match, \
        'Expected query string arguments {!r}, got {!r}'.format(
            api_call.query_string_args,
            query_string_args,
            )

    http_methods_match = api_call.http_method == http_method
    assert http_methods_match, \
        'Expected HTTP method {!r}, got {!r}'.format(
            api_call.http_method,
            http_method,
            )

    request_body_deserializations_match = \
        api_call.request_body_deserialization == request_body_deserialization
    assert request_body_deserializations_match, \
        'Expected request body deserialization {!r}, got {!r}'.format(
            api_call.request_body_deserialization,
            request_body_deserialization,
            )


def _convert_object_strings_to_unicode(object_):
    if isinstance(object_, str):
        object_converted = text(object_)
    elif isinstance(object_, (list, tuple)):
        object_converted = \
            [_convert_object_strings_to_unicode(value) for value in object_]
    elif isinstance(object_, dict):
        object_converted = {}
        for key, value in object_.items():
            object_converted[_convert_object_strings_to_unicode(key)] = \
                _convert_object_strings_to_unicode(value)
    else:
        object_converted = object_

    return object_converted
