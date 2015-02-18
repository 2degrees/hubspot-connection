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

from httplib import ACCEPTED as HTTP_STATUS_ACCEPTED
from httplib import NO_CONTENT as HTTP_STATUS_NO_CONTENT
from httplib import OK as HTTP_STATUS_OK
from httplib import UNAUTHORIZED as HTTP_STATUS_UNAUTHORIZED
from json import dumps as json_serialize
from urllib import urlencode
from urlparse import parse_qs
from urlparse import urlsplit
from urlparse import urlunsplit

from pkg_resources import get_distribution
from pyrecord import Record
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase
from requests.sessions import Session
from voluptuous import Schema

from hubspot.connection._validators import Constant
from hubspot.connection.exc import HubspotAuthenticationError
from hubspot.connection.exc import HubspotClientError
from hubspot.connection.exc import HubspotServerError
from hubspot.connection.exc import HubspotUnsupportedResponseError


_DISTRIBUTION_NAME = 'hubspot-connection'
_DISTRIBUTION_VERSION = get_distribution(_DISTRIBUTION_NAME).version
_USER_AGENT = 'HubSpot Python Client/' + _DISTRIBUTION_VERSION


_HUBSPOT_ERROR_RESPONSE_SCHEMA = Schema(
    {
        'status': Constant('error'),
        'message': unicode,
        'requestId': unicode,
        },
    required=True,
    extra=True,
    )


_HTTP_CONNECTION_MAX_RETRIES = 3


_HTTP_STATUS_CODES_WITH_EMPTY_BODIES = \
    frozenset((HTTP_STATUS_ACCEPTED, HTTP_STATUS_NO_CONTENT))


class PortalConnection(object):
    """
    Connection to HubSpot

    :param authentication_key: This can be either an :class:`APIKey` or an \
            :class:`OAuthKey` instance
    :param basestring change_source: The string passed to HubSpot as \
            ``auditId`` in the query string
    """
    _API_URL = 'https://api.hubapi.com'

    def __init__(self, authentication_key, change_source):
        super(PortalConnection, self).__init__()

        self._authentication_handler = \
            _QueryStringAuthenticationHandler(authentication_key)
        self._change_source = change_source

        self._session = Session()
        self._session.headers['User-Agent'] = _USER_AGENT

        http_adapter = HTTPAdapter(max_retries=_HTTP_CONNECTION_MAX_RETRIES)
        self._session.mount('', http_adapter)

    def send_get_request(self, url_path, query_string_args=None):
        """
        Send a GET request to HubSpot

        :param basestring url_path: The URL path to the endpoint
        :param dict query_string_args: The query string arguments

        :return: Decoded version of the ``JSON`` that HubSpot put in \
                the body of the response.

        """
        return self._send_request('GET', url_path, query_string_args)

    def send_post_request(self, url_path, body_deserialization):
        """
        Send a POST request to HubSpot

        :param basestring url_path: The URL path to the endpoint
        :param dict body_deserialization: The request's body message \
            deserialized

        :return: Decoded version of the ``JSON`` that HubSpot put in \
                the body of the response.
        """
        return self._send_request(
            'POST',
            url_path,
            body_deserialization=body_deserialization,
            )

    def send_put_request(self, url_path, body_deserialization):
        """
        Send a PUT request to HubSpot

        :param basestring url_path: The URL path to the endpoint
        :param body_deserialization: The request's body message deserialized

        :return: Decoded version of the ``JSON`` that HubSpot put in \
                the body of the response.
        """
        return self._send_request(
            'PUT',
            url_path,
            body_deserialization=body_deserialization,
            )

    def send_delete_request(self, url_path):
        """
        Send a DELETE request to HubSpot

        :param basestring url_path: The URL path to the endpoint

        :return: Decoded version of the ``JSON`` that HubSpot put in \
                the body of the response.
        """
        return self._send_request('DELETE', url_path)

    def _send_request(
        self,
        method,
        url_path,
        query_string_args=None,
        body_deserialization=None,
        ):
        url = self._API_URL + url_path

        query_string_args = query_string_args or {}
        query_string_args = dict(query_string_args, auditId=self._change_source)

        request_headers = \
            {'content-type': 'application/json'} if body_deserialization else {}

        if body_deserialization:
            request_body_serialization = json_serialize(body_deserialization)
        else:
            request_body_serialization = None

        response = self._session.request(
            method,
            url,
            params=query_string_args,
            auth=self._authentication_handler,
            data=request_body_serialization,
            headers=request_headers,
            )

        response_body_deserialization = \
            self._deserialize_response_body(response)
        return response_body_deserialization

    @classmethod
    def _deserialize_response_body(cls, response):
        cls._require_successful_response(response)

        if response.status_code == HTTP_STATUS_OK:
            cls._require_json_response(response)
            response_body_deserialization = response.json() or None
        elif response.status_code in _HTTP_STATUS_CODES_WITH_EMPTY_BODIES:
            response_body_deserialization = None
        else:
            exception_message = \
                'Unsupported response status {}'.format(response.status_code)
            raise HubspotUnsupportedResponseError(exception_message)

        return response_body_deserialization

    @staticmethod
    def _require_successful_response(response):
        if 400 <= response.status_code < 500:
            response_data = response.json()
            error_data = _HUBSPOT_ERROR_RESPONSE_SCHEMA(response_data)

            if response.status_code == HTTP_STATUS_UNAUTHORIZED:
                exception_class = HubspotAuthenticationError
            else:
                exception_class = HubspotClientError
            raise exception_class(
                error_data['message'],
                error_data['requestId'],
                )
        elif 500 <= response.status_code < 600:
            raise HubspotServerError(response.reason, response.status_code)

    @staticmethod
    def _require_json_response(response):
        content_type_header_value = response.headers.get('Content-Type')
        if not content_type_header_value:
            exception_message = 'Response does not specify a Content-Type'
            raise HubspotUnsupportedResponseError(exception_message)

        content_type = content_type_header_value.split(';')[0].lower()
        if content_type != 'application/json':
            exception_message = \
                'Unsupported response content type {}'.format(content_type)
            raise HubspotUnsupportedResponseError(exception_message)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._session.close()


_AuthenticationKey = Record.create_type('_AuthenticationKey', 'key_value')

OAuthKey = _AuthenticationKey.extend_type('OAuthKey')

APIKey = _AuthenticationKey.extend_type('APIKey')


class _QueryStringAuthenticationHandler(AuthBase):

    _KEY_NAME_BY_AUTHN_TYPE = {
        OAuthKey: 'access_token',
        APIKey: 'hapikey',
        }

    def __init__(self, authentication_key, *args, **kwargs):
        super(_QueryStringAuthenticationHandler, self).__init__(*args, **kwargs)

        authentication_type = authentication_key.__class__
        self._key_name = self._KEY_NAME_BY_AUTHN_TYPE[authentication_type]
        self._key_value = authentication_key.key_value

    def __call__(self, request):
        request.url = _add_query_string_arg_to_url(
            self._key_name,
            self._key_value,
            request.url,
            )
        return request


def _add_query_string_arg_to_url(
    query_string_arg_name,
    query_string_arg_value,
    url,
    ):
    url_parts = urlsplit(url)
    query_string_args = parse_qs(url_parts.query)
    query_string_args[query_string_arg_name] = query_string_arg_value
    query_string_raw = urlencode(query_string_args, doseq=True)

    url = urlunsplit((
        url_parts.scheme,
        url_parts.netloc,
        url_parts.path,
        query_string_raw,
        url_parts.fragment,
        ))
    return url
