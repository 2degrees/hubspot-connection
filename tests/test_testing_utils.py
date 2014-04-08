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

from nose.tools import assert_is_instance
from nose.tools import assert_raises
from nose.tools import eq_

from hubspot.connection.testing import ConstantMultiResponseDataMaker
from hubspot.connection.testing import ConstantResponseDataMaker
from hubspot.connection.testing import MockPortalConnection
from hubspot.connection.testing import RemoteMethod
from hubspot.connection.testing import RemoteMethodInvocation


_STUB_PATH_INFO = '/foo'

_STUB_RESPONSE_DATA = {'foo': 'bar'}

_STUB_RESPONSE_DATA_MAKER = ConstantResponseDataMaker(_STUB_RESPONSE_DATA)


class TestMockPortalConnection(object):

    def test_get_request(self):
        remote_method = RemoteMethod(_STUB_PATH_INFO, 'GET')
        connection = self._make_connection_for_remote_method(remote_method)

        response_data = connection.send_get_request(_STUB_PATH_INFO)

        expected_remote_method_invocation = \
            RemoteMethodInvocation(remote_method)
        self._assert_sole_remote_method_invocation_equals(
            expected_remote_method_invocation,
            connection,
            )

        eq_(_STUB_RESPONSE_DATA, response_data)

    def test_get_request_with_query_string_args(self):
        remote_method = RemoteMethod(_STUB_PATH_INFO, 'GET')
        connection = self._make_connection_for_remote_method(remote_method)

        query_string_args = {'foo': 'bar'}
        response_data = \
            connection.send_get_request(_STUB_PATH_INFO, query_string_args)

        expected_remote_method_invocation = \
            RemoteMethodInvocation(remote_method, query_string_args)
        self._assert_sole_remote_method_invocation_equals(
            expected_remote_method_invocation,
            connection,
            )

        eq_(_STUB_RESPONSE_DATA, response_data)

    def test_post_request(self):
        remote_method = RemoteMethod(_STUB_PATH_INFO, 'POST')
        connection = self._make_connection_for_remote_method(remote_method)

        body_deserialization = {'foo': 'bar'}
        response_data = \
            connection.send_post_request(_STUB_PATH_INFO, body_deserialization)

        expected_remote_method_invocation = RemoteMethodInvocation(
            remote_method,
            body_deserialization=body_deserialization,
            )
        self._assert_sole_remote_method_invocation_equals(
            expected_remote_method_invocation,
            connection,
            )

        eq_(_STUB_RESPONSE_DATA, response_data)

    def test_put_request(self):
        remote_method = RemoteMethod(_STUB_PATH_INFO, 'PUT')
        connection = self._make_connection_for_remote_method(remote_method)

        body_deserialization = {'foo': 'bar'}
        response_data = \
            connection.send_put_request(_STUB_PATH_INFO, body_deserialization)

        expected_remote_method_invocation = RemoteMethodInvocation(
            remote_method,
            body_deserialization=body_deserialization,
            )
        self._assert_sole_remote_method_invocation_equals(
            expected_remote_method_invocation,
            connection,
            )

        eq_(_STUB_RESPONSE_DATA, response_data)

    def test_delete_request(self):
        remote_method = RemoteMethod(_STUB_PATH_INFO, 'DELETE')
        connection = self._make_connection_for_remote_method(remote_method)

        response_data = connection.send_delete_request(_STUB_PATH_INFO)

        expected_remote_method_invocation = \
            RemoteMethodInvocation(remote_method)
        self._assert_sole_remote_method_invocation_equals(
            expected_remote_method_invocation,
            connection,
            )

        eq_(_STUB_RESPONSE_DATA, response_data)

    def test_no_response_data_maker(self):
        connection = MockPortalConnection()

        response_data = connection.send_get_request(_STUB_PATH_INFO)

        eq_(None, response_data)

    def test_response_data_strings(self):
        """Strings in the response data are converted to unicode"""
        remote_method = RemoteMethod(_STUB_PATH_INFO, 'GET')
        connection = self._make_connection_for_remote_method(remote_method)

        response_data = connection.send_get_request(_STUB_PATH_INFO)
        string_values = response_data.keys() + response_data.values()
        for string_value in string_values:
            assert_is_instance(string_value, unicode)

    def _make_connection_for_remote_method(self, remote_method):
        response_data_maker_by_remote_method = \
            {remote_method: _STUB_RESPONSE_DATA_MAKER}
        connection = MockPortalConnection(response_data_maker_by_remote_method)
        return connection

    def _assert_sole_remote_method_invocation_equals(
        self,
        expected_remote_method_invocation,
        connection,
        ):
        eq_(
            [expected_remote_method_invocation],
            connection.remote_method_invocations,
            )

    def test_remote_method_invocation_filtering(self):
        connection = MockPortalConnection()

        connection.send_post_request(_STUB_PATH_INFO, None)
        connection.send_get_request(_STUB_PATH_INFO)
        connection.send_post_request(_STUB_PATH_INFO, _STUB_RESPONSE_DATA)

        remote_method1 = RemoteMethod(_STUB_PATH_INFO, 'POST')
        filtered_remote_method1_invocations = \
            connection.get_invocations_for_remote_method(remote_method1)
        expected_filtered_remote_method1_invocations = [
            RemoteMethodInvocation(remote_method1),
            RemoteMethodInvocation(remote_method1, None, _STUB_RESPONSE_DATA),
            ]
        eq_(
            filtered_remote_method1_invocations,
            expected_filtered_remote_method1_invocations,
            )

        remote_method2 = RemoteMethod(_STUB_PATH_INFO, 'GET')
        filtered_remote_method2_invocations = \
            connection.get_invocations_for_remote_method(remote_method2)
        expected_filtered_remote_method2_invocations = \
            [RemoteMethodInvocation(remote_method2)]
        eq_(
            expected_filtered_remote_method2_invocations,
            filtered_remote_method2_invocations,
            )


def test_constant_response_data_maker():
    response_data_maker = ConstantResponseDataMaker(_STUB_RESPONSE_DATA)
    response_data = response_data_maker(None, None)
    eq_(_STUB_RESPONSE_DATA, response_data)


class TestConstantMultiResponseDataMaker(object):

    _STUB_RESPONSE2_DATA = None

    _STUB_RESPONSES_DATA = [
        _STUB_RESPONSE_DATA,
        _STUB_RESPONSE2_DATA,
        ]

    def setup(self):
        self.response_data_maker = \
            ConstantMultiResponseDataMaker(self._STUB_RESPONSES_DATA)

    def test_single_request(self):
        response_data = self.response_data_maker(None, None)
        eq_(_STUB_RESPONSE_DATA, response_data)

    def test_multiple_requests(self):
        response1_data = self.response_data_maker(None, None)
        eq_(_STUB_RESPONSE_DATA, response1_data)

        response2_data = self.response_data_maker(None, None)
        eq_(self._STUB_RESPONSE2_DATA, response2_data)

    def test_too_many_requests(self):
        self.response_data_maker(None, None)
        self.response_data_maker(None, None)

        with assert_raises(IndexError):
            self.response_data_maker(None, None)
