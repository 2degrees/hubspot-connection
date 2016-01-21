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

from nose.tools import assert_false
from nose.tools import assert_is_instance
from nose.tools import assert_raises
from nose.tools import eq_

from hubspot.connection.exc import HubspotAuthenticationError
from hubspot.connection.testing import MockPortalConnection
from hubspot.connection.testing import SuccessfulAPICall
from hubspot.connection.testing import UnsuccessfulAPICall

from tests.utils import assert_raises_substring
from tests.utils import get_uuid4_str


_STUB_URL_PATH = '/foo'

_STUB_RESPONSE_BODY_DESERIALIZATION = {'foo': 'bar'}

_STUB_API_CALL_1 = SuccessfulAPICall(
    _STUB_URL_PATH,
    'GET',
    response_body_deserialization=_STUB_RESPONSE_BODY_DESERIALIZATION,
    )

_STUB_API_CALL_2 = SuccessfulAPICall(
    _STUB_URL_PATH,
    'POST',
    response_body_deserialization=_STUB_RESPONSE_BODY_DESERIALIZATION,
    )


class TestMockPortalConnection(object):

    def test_get_request(self):
        connection = \
            self._make_connection_for_expected_api_call(_STUB_API_CALL_1)

        response_body_deserialization = \
            connection.send_get_request(_STUB_URL_PATH)

        self._assert_sole_api_call_equals(_STUB_API_CALL_1, connection)
        eq_(_STUB_RESPONSE_BODY_DESERIALIZATION, response_body_deserialization)

    def test_get_request_with_query_string_args(self):
        query_string_args = {'foo': 'bar'}
        expected_api_call = SuccessfulAPICall(
            _STUB_URL_PATH,
            'GET',
            query_string_args,
            response_body_deserialization=_STUB_RESPONSE_BODY_DESERIALIZATION,
            )
        connection = \
            self._make_connection_for_expected_api_call(expected_api_call)

        connection.send_get_request(_STUB_URL_PATH, query_string_args)

        self._assert_sole_api_call_equals(expected_api_call, connection)

    def test_post_request(self):
        request_body_deserialization = {'foo': 'bar'}
        expected_api_call = SuccessfulAPICall(
            _STUB_URL_PATH,
            'POST',
            request_body_deserialization=request_body_deserialization,
            response_body_deserialization=_STUB_RESPONSE_BODY_DESERIALIZATION,
            )
        connection = \
            self._make_connection_for_expected_api_call(expected_api_call)

        response_body_deserialization = connection.send_post_request(
            _STUB_URL_PATH,
            request_body_deserialization,
            )

        self._assert_sole_api_call_equals(expected_api_call, connection)
        eq_(_STUB_RESPONSE_BODY_DESERIALIZATION, response_body_deserialization)

    def test_put_request(self):
        request_body_deserialization = {'foo': 'bar'}
        expected_api_call = SuccessfulAPICall(
            _STUB_URL_PATH,
            'PUT',
            request_body_deserialization=request_body_deserialization,
            response_body_deserialization=_STUB_RESPONSE_BODY_DESERIALIZATION,
            )
        connection = \
            self._make_connection_for_expected_api_call(expected_api_call)

        response_body_deserialization = connection.send_put_request(
            _STUB_URL_PATH,
            request_body_deserialization,
            )

        self._assert_sole_api_call_equals(expected_api_call, connection)
        eq_(_STUB_RESPONSE_BODY_DESERIALIZATION, response_body_deserialization)

    def test_delete_request(self):
        expected_api_call = SuccessfulAPICall(
            _STUB_URL_PATH,
            'DELETE',
            response_body_deserialization=_STUB_RESPONSE_BODY_DESERIALIZATION,
            )
        connection = \
            self._make_connection_for_expected_api_call(expected_api_call)

        response_body_deserialization = \
            connection.send_delete_request(_STUB_URL_PATH)

        self._assert_sole_api_call_equals(expected_api_call, connection)
        eq_(_STUB_RESPONSE_BODY_DESERIALIZATION, response_body_deserialization)

    def test_response_data_strings(self):
        """Strings in the response data are converted to unicode"""
        connection = \
            self._make_connection_for_expected_api_call(_STUB_API_CALL_1)

        response_body_deserialization = \
            connection.send_get_request(_STUB_URL_PATH)

        # Inspect returned data
        _assert_dict_keys_and_values_are_unicode(response_body_deserialization)

        # Inspect stored data
        api_call = connection.api_calls[0]
        _assert_dict_keys_and_values_are_unicode(
            api_call.response_body_deserialization,
            )

    def test_multiple_api_calls_simulators(self):
        connection = MockPortalConnection(
            _ConstantCallable([_STUB_API_CALL_1]),
            _ConstantCallable([_STUB_API_CALL_2]),
            )

        assert_false(connection.api_calls)

        connection.send_get_request(_STUB_URL_PATH)
        eq_([_STUB_API_CALL_1], connection.api_calls)

        connection.send_post_request(_STUB_URL_PATH, None)
        eq_([_STUB_API_CALL_1, _STUB_API_CALL_2], connection.api_calls)

    def test_multiple_api_calls(self):
        connection = MockPortalConnection(
            _ConstantCallable([_STUB_API_CALL_1, _STUB_API_CALL_2]),
            )

        assert_false(connection.api_calls)

        connection.send_get_request(_STUB_URL_PATH)
        eq_([_STUB_API_CALL_1], connection.api_calls)

        connection.send_post_request(_STUB_URL_PATH, None)
        eq_([_STUB_API_CALL_1, _STUB_API_CALL_2], connection.api_calls)

    def test_unsuccessful_api_call(self):
        exception = \
            HubspotAuthenticationError('Must authenticate', get_uuid4_str(), {})
        expected_api_call = UnsuccessfulAPICall(
            _STUB_URL_PATH,
            'GET',
            exception=exception,
            )
        connection = \
            self._make_connection_for_expected_api_call(expected_api_call)

        with assert_raises(type(exception)) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        eq_(exception, context_manager.exception)
        self._assert_sole_api_call_equals(expected_api_call, connection)

    def test_too_few_requests(self):
        connection = \
            self._make_connection_for_expected_api_call(_STUB_API_CALL_1)
        error_message = '1 more requests were expected'
        with assert_raises_substring(AssertionError, error_message):
            with connection:
                # Do not make any requests in the connection
                pass

    def test_correct_number_of_requests(self):
        connection = \
            self._make_connection_for_expected_api_call(_STUB_API_CALL_1)
        with connection:
            connection.send_get_request(_STUB_URL_PATH)

    def test_too_many_requests(self):
        connection = MockPortalConnection()
        error_message = \
            'Not enough API calls for new requests (requested {!r})'.format(
                _STUB_URL_PATH,
                )
        with assert_raises_substring(AssertionError, error_message):
            connection.send_get_request(_STUB_URL_PATH)

    def test_exception_inside_context_manager(self):
        """The validation for the number of requests is skipped."""
        connection = \
            self._make_connection_for_expected_api_call(_STUB_API_CALL_1)
        error_message = 'Foo'
        with assert_raises_substring(AssertionError, error_message):
            with connection:
                assert False, error_message

    def test_unexpected_url_path(self):
        connection = \
            self._make_connection_for_expected_api_call(_STUB_API_CALL_1)

        url_path = _STUB_URL_PATH + '/foo'
        error_message = 'Expected URL path {!r}, got {!r}'.format(
            _STUB_URL_PATH,
            url_path,
            )
        with assert_raises_substring(AssertionError, error_message):
            connection.send_get_request(url_path)

    def test_unexpected_http_method(self):
        connection = \
            self._make_connection_for_expected_api_call(_STUB_API_CALL_1)

        error_message = "Expected HTTP method 'GET', got 'POST'"
        with assert_raises_substring(AssertionError, error_message):
            connection.send_post_request(_STUB_URL_PATH, None)

    def test_unexpected_query_string_args(self):
        connection = \
            self._make_connection_for_expected_api_call(_STUB_API_CALL_1)

        query_string_args = {'a': 'b'}
        error_message = 'Expected query string arguments {!r}, got {!r}' \
            .format(None, query_string_args)
        with assert_raises_substring(AssertionError, error_message):
            connection.send_get_request(_STUB_URL_PATH, query_string_args)

    def test_unexpected_request_body_deserialization(self):
        expected_api_call = SuccessfulAPICall(
            _STUB_URL_PATH,
            'PUT',
            response_body_deserialization=_STUB_RESPONSE_BODY_DESERIALIZATION,
            )
        connection = \
            self._make_connection_for_expected_api_call(expected_api_call)

        request_body_deserialization = {'a': 'b'}
        error_message = 'Expected request body deserialization {!r}, got {!r}' \
            .format(None, request_body_deserialization)
        with assert_raises_substring(AssertionError, error_message):
            connection.send_put_request(
                _STUB_URL_PATH,
                request_body_deserialization,
                )

    @staticmethod
    def _make_connection_for_expected_api_call(expected_api_call):
        expected_api_calls_simulator = _ConstantCallable([expected_api_call])
        connection = MockPortalConnection(expected_api_calls_simulator)
        return connection

    @staticmethod
    def _assert_sole_api_call_equals(expected_api_call, connection):
        eq_([expected_api_call], connection.api_calls)


def _assert_dict_keys_and_values_are_unicode(dict_):
    values = dict_.keys() + dict_.values()
    for value in values:
        assert_is_instance(value, unicode)


class _ConstantCallable(object):

    def __init__(self, return_value):
        super(_ConstantCallable, self).__init__()

        self._return_value = return_value

    def __call__(self):
        return self._return_value
