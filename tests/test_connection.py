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
from abc import abstractmethod
from abc import ABCMeta

from builtins import bytes

from json import dumps as json_serialize

from six import with_metaclass
from six.moves.urllib.parse import parse_qs
from six.moves.urllib.parse import urlparse

from nose.tools import assert_dict_contains_subset
from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_in
from nose.tools import assert_is_instance
from nose.tools import assert_raises
from nose.tools import eq_
from nose.tools import ok_
from requests.adapters import HTTPAdapter as RequestsHTTPAdapter
from requests.models import Response as RequestsResponse

from hubspot.connection import APIKey
from hubspot.connection import OAuthKey
from hubspot.connection import PortalConnection
from hubspot.connection.exc import HubspotAuthenticationError
from hubspot.connection.exc import HubspotClientError
from hubspot.connection.exc import HubspotCorruptedResponseError
from hubspot.connection.exc import HubspotServerError
from hubspot.connection.exc import HubspotUnsupportedResponseError

from tests.utils import get_uuid4_str


_STUB_URL_PATH = '/foo'

_STUB_AUTHENTICATION_KEY = APIKey(get_uuid4_str())


class TestPortalConnection(object):

    def test_get_request(self):
        self._check_request_sender('GET', 'send_get_request', False)

    def test_post_request(self):
        self._check_request_sender('POST', 'send_post_request', True)

    def test_put_request(self):
        self._check_request_sender('PUT', 'send_put_request', True)

    def test_delete_request(self):
        self._check_request_sender('DELETE', 'send_delete_request', False)

    @staticmethod
    def _check_request_sender(
        http_method_name,
        request_sender_name,
        include_request_body,
        ):
        connection = _MockPortalConnection()

        body_deserialization = {'foo': 'bar'} if include_request_body else None

        request_sender = getattr(connection, request_sender_name)
        request_sender_kwargs = {}
        if include_request_body:
            request_sender_kwargs['body_deserialization'] = body_deserialization
        request_sender(_STUB_URL_PATH, **request_sender_kwargs)

        eq_(1, len(connection.prepared_requests))

        prepared_request = connection.prepared_requests[0]
        eq_(http_method_name, prepared_request.method)

        if include_request_body:
            assert_in('content-type', prepared_request.headers)
            assert_equal(
                'application/json',
                prepared_request.headers['content-type']
            )

        requested_url_path = _get_path_from_api_url(prepared_request.url)
        eq_(_STUB_URL_PATH, requested_url_path)

        if include_request_body:
            body_serialization = json_serialize(body_deserialization)
            eq_(body_serialization, prepared_request.body)
        else:
            assert_false(prepared_request.body)

    def test_user_agent(self):
        connection = _MockPortalConnection()

        connection.send_get_request(_STUB_URL_PATH)

        prepared_request = connection.prepared_requests[0]
        assert_in('User-Agent', prepared_request.headers)

        user_agent_header_value = prepared_request.headers['User-Agent']
        ok_(user_agent_header_value.startswith('HubSpot Python Client/'))

    def test_change_source(self):
        change_source = get_uuid4_str()
        connection = _MockPortalConnection(change_source=change_source)

        connection.send_get_request(_STUB_URL_PATH)

        prepared_request = connection.prepared_requests[0]
        query_string_args = \
            _get_query_string_args_from_url(prepared_request.url)
        expected_change_source_args = {'auditId': [change_source]}
        assert_dict_contains_subset(
            expected_change_source_args,
            query_string_args,
            )

    def test_with_extra_query_string_args(self):
        """
        Any extra query string argument co-exists with authentication-related
        arguments.

        """
        connection = _MockPortalConnection()

        extra_query_string_args = {'foo': ['bar']}
        connection.send_get_request(_STUB_URL_PATH, extra_query_string_args)

        prepared_request = connection.prepared_requests[0]
        query_string_args = \
            _get_query_string_args_from_url(prepared_request.url)
        assert_dict_contains_subset(extra_query_string_args, query_string_args)

    def test_json_response(self):
        """
        The output of "200 OK" responses with a JSON body is that body
        deserialized.

        """
        expected_body_deserialization = {'foo': 'bar'}
        response_data_maker = _ResponseMaker(
            200,
            expected_body_deserialization,
            'application/json',
        )
        connection = _MockPortalConnection(response_data_maker)

        response_data = connection.send_get_request(_STUB_URL_PATH)

        eq_(expected_body_deserialization, response_data)

    def test_corrupted_json_response(self):
        """An exception is raised for responses containing malformed JSON."""
        response_data_maker = _CorruptJSONResponseMaker(200)
        connection = _MockPortalConnection(response_data_maker)

        with assert_raises(HubspotCorruptedResponseError) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        exception = context_manager.exception
        eq_('Corrupt JSON in response body', str(exception))

    def test_unexpected_response_status_code(self):
        """
        An exception is raised when the response status code is unsupported.

        """
        unsupported_response_data_maker = _ResponseMaker(304)
        connection = _MockPortalConnection(unsupported_response_data_maker)

        with assert_raises(HubspotUnsupportedResponseError) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        exception = context_manager.exception
        eq_('Unsupported response status 304', str(exception))

    def test_unexpected_response_content_type(self):
        """
        An exception is raised when the response status code is 200 but the
        content type is not "application/json".

        """
        unsupported_response_data_maker = \
            _ResponseMaker(200, 'Text', 'text/plain')
        connection = _MockPortalConnection(unsupported_response_data_maker)

        with assert_raises(HubspotUnsupportedResponseError) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        exception = context_manager.exception
        eq_('Unsupported response content type text/plain', str(exception))

    def test_missing_response_content_type(self):
        """An exception is raised when the content type is missing."""
        unsupported_response_data_maker = _ResponseMaker(200, 'Text')
        connection = _MockPortalConnection(unsupported_response_data_maker)

        with assert_raises(HubspotUnsupportedResponseError) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        exception = context_manager.exception
        eq_('Response does not specify a Content-Type', str(exception))

    def test_missing_response_content_type_and_content_length_is_zero(self):
        response_data_maker = _ResponseMaker(202, '')
        connection = _MockPortalConnection(response_data_maker)

        response_data = connection.send_get_request(_STUB_URL_PATH)

        eq_(None, response_data)

    def test_response_content_length_is_zero(self):
        response_data_maker = _ResponseMaker(200, '', 'application/json')
        connection = _MockPortalConnection(response_data_maker)

        response_data = connection.send_get_request(_STUB_URL_PATH)

        eq_(None, response_data)

    def test_no_content_response(self):
        """There's no output for "204 NO CONTENT" responses."""
        connection = _MockPortalConnection()

        response_data = connection.send_get_request(_STUB_URL_PATH)

        eq_(None, response_data)

    def test_context_manager(self):
        with _MockPortalConnection() as connection:
            assert_is_instance(connection, _MockPortalConnection)

        assert_false(connection.adapter.is_open)

    def test_keep_alive(self):
        connection = _MockPortalConnection()
        connection.send_get_request(_STUB_URL_PATH)
        ok_(connection.adapter.is_keep_alive_always_used)


class TestErrorResponses(object):

    def test_server_error_response(self):
        response_data_maker = _ResponseMaker(500)
        connection = _MockPortalConnection(response_data_maker)
        with assert_raises(HubspotServerError) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        exception = context_manager.exception
        eq_(500, exception.http_status_code)
        eq_('500 Reason', repr(exception))

    def test_client_error_response(self):
        request_id = get_uuid4_str()
        error_message = 'Json node is missing child property'
        body_deserialization = {
            'status': 'error',
            'message': error_message,
            'requestId': request_id,
            }
        response_data_maker = _ResponseMaker(400, body_deserialization)
        connection = _MockPortalConnection(response_data_maker)

        with assert_raises(HubspotClientError) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        exception = context_manager.exception
        eq_(request_id, exception.request_id)
        eq_(error_message, str(exception))

    def test_corrupted_json_response(self):
        """An exception is raised for responses containing malformed JSON."""
        response_data_maker = _CorruptJSONResponseMaker(400)
        connection = _MockPortalConnection(response_data_maker)

        with assert_raises(HubspotCorruptedResponseError) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        exception = context_manager.exception
        eq_('Corrupt JSON in response body', str(exception))


class TestAuthentication(object):

    def test_oauth_token(self):
        self._assert_credentials_set_in_request(OAuthKey, 'access_token')

    def test_api_key(self):
        self._assert_credentials_set_in_request(APIKey, 'hapikey')

    @staticmethod
    def _assert_credentials_set_in_request(key_class, expected_key_name):
        authentication_key_value = get_uuid4_str()
        authentication_key = key_class(authentication_key_value)
        connection = \
            _MockPortalConnection(authentication_key=authentication_key)

        connection.send_get_request(_STUB_URL_PATH)

        expected_credentials = {expected_key_name: [authentication_key_value]}
        prepared_request = connection.prepared_requests[0]
        query_string_args = \
            _get_query_string_args_from_url(prepared_request.url)
        assert_dict_contains_subset(expected_credentials, query_string_args)

    def test_unauthorized_response(self):
        request_id = get_uuid4_str()
        error_message = 'Invalid credentials'
        response_data_maker = _ResponseMaker(
            401,
            {
                'status': 'error',
                'message': error_message,
                'requestId': request_id,
                },
            )
        connection = _MockPortalConnection(
            response_data_maker,
            authentication_key=_STUB_AUTHENTICATION_KEY,
            )

        with assert_raises(HubspotAuthenticationError) as context_manager:
            connection.send_get_request(_STUB_URL_PATH)

        exception = context_manager.exception

        eq_(request_id, exception.request_id)
        eq_(error_message, str(exception))


class _MockPortalConnection(PortalConnection):

    def __init__(
        self,
        response_data_maker=None,
        authentication_key=_STUB_AUTHENTICATION_KEY,
        change_source=None,
        *args,
        **kwargs
    ):
        super_class = super(_MockPortalConnection, self)
        super_class.__init__(authentication_key, change_source, *args, **kwargs)

        self.adapter = _MockRequestsAdapter(response_data_maker)
        self._session.mount(self._API_URL, self.adapter)

    @property
    def prepared_requests(self):
        return self.adapter.prepared_requests


class _MockRequestsAdapter(RequestsHTTPAdapter):

    def __init__(self, response_data_maker=None, *args, **kwargs):
        super(_MockRequestsAdapter, self).__init__(*args, **kwargs)

        self._response_data_maker = \
            response_data_maker or _NO_CONTENT_RESPONSE_MAKER

        self.prepared_requests = []
        self.is_keep_alive_always_used = True
        self.is_open = True

    def send(self, request, stream=False, *args, **kwargs):
        is_keep_alive_implied = not stream
        self.is_keep_alive_always_used &= is_keep_alive_implied

        self.prepared_requests.append(request)

        response = self._response_data_maker(request)
        return response

    def close(self, *args, **kwargs):
        self.is_open = False

        return super(_MockRequestsAdapter, self).close(*args, **kwargs)


class _BaseResponseMaker(with_metaclass(ABCMeta, object)):

    def __init__(self, status_code):
        super(_BaseResponseMaker, self).__init__()
        self._status_code = status_code

    @abstractmethod
    def __call__(self, request):
        response = RequestsResponse()
        response.status_code = self._status_code
        response.reason = 'Reason'
        return response


class _ResponseMaker(_BaseResponseMaker):

    def __init__(
        self,
        status_code,
        body_deserialization=None,
        content_type=None,
    ):
        super(_ResponseMaker, self).__init__(status_code)

        self._body_deserialization = body_deserialization
        self._content_type = content_type

    def __call__(self, request):
        response = super(_ResponseMaker, self).__call__(request)

        if self._content_type:
            content_type_header_value = \
                '{}; charset=UTF-8'.format(self._content_type)
            response.headers['Content-Type'] = content_type_header_value

        if self._status_code != 204 and self._body_deserialization is not None:
            response._content = \
                bytes(json_serialize(self._body_deserialization), 'UTF-8')

        return response


class _CorruptJSONResponseMaker(_BaseResponseMaker):

    def __call__(self, request):
        response = super(_CorruptJSONResponseMaker, self).__call__(request)
        response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        response._content = bytes('{not json', 'UTF-8')
        return response


_NO_CONTENT_RESPONSE_MAKER = _ResponseMaker(204)


def _get_path_from_api_url(api_url):
    assert api_url.startswith(PortalConnection._API_URL)

    api_url_length = len(PortalConnection._API_URL)
    api_url_path_and_query_string = api_url[api_url_length:]
    api_url_path = api_url_path_and_query_string.split('?')[0]
    return api_url_path


def _get_query_string_args_from_url(url):
    url_parts = urlparse(url)
    query_string_raw = url_parts.query
    if query_string_raw:
        query_string_args = parse_qs(query_string_raw, strict_parsing=True)
    else:
        query_string_args = {}
    return query_string_args
