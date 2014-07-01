HubSpot connection for API clients
**********************************

:Sponsored by: `2degrees Limited <http://dev.2degreesnetwork.com/>`_
:Latest release: |release|

**hubspot-connection** provides a lightweight abstraction layer for making
requests to the HubSpot API.

**Example:**

.. code-block:: python

    from hubspot.connection import APIKey
    from hubspot.connection import PortalConnection

    authentication_key = APIKey('HUBSPOT-API-KEY')
    with PortalConnection(authentication_key, 'client') as connection:
        contacts_data = connection.send_get_request('/contacts/v1/contacts/statistics')
        print "Number of contacts: {}".format(contacts_data.get('contacts'))

Tutorial
--------

Authentication
++++++++++++++

HubSpot supports two authentication methods: OAuth and a proprietary,
token-based method referred to as "API Key".

In order to authenticate you just need to instanciate either
:mod:`hubspot.connection.OAuthKey` or :mod:`hubspot.connection.APIKey` with the
apropriate value.

**Example:**

.. code-block:: python

    authentication_key = OAuthKey('HUBSPOT-OAUTH-KEY')

    authentication_key = APIKey('HUBSPOT-API-KEY')


How to make requests to HubSpot
+++++++++++++++++++++++++++++++

:class:`~hubspot.connection.PortalConnection` is meant to be used as a context
manager which takes care of keeping the connection alive retrying a maximum of
3 times should there be any network-level timeout or socket errors.

A good example of a library using :mod:`hubspot.connection` can be seen here:
`hubspot-contacts <https://github.com/2degrees/hubspot-contacts>`_.


Testing
-------

`hubspot-connection` comes bundled with utilities designed to help you with
testing.

The :class:`~hubspot.connection.testing.MockPortalConnection` is initialized
with zero or more so-called "api call simulators" (or simply "simulators"),
which are passed by position. Simulators are callables that receive no
arguments and return an iterable of successful or unsuccessful API calls.

Their role, is to tell the
:class:`~hubspot.connection.testing.MockPortalConnection` what API calls are
excepted to be called, and that each will have exactly the expected:

- URL path
- Body deserialization
- URL arguments
- Method

If the response is expected to be successful, it's body deserialization will be
verified, if the response is expected to be unsuccessful, the exception will be
checked, whether it's the correct one. To represent API calls this library
comes with :class:`~hubspot.connection.testing.SuccessfulAPICall` and
:class:`~hubspot.connection.testing.UnsuccessfulAPICall`.

Should any unexpected API end-point get called, any of the expected end-points
is not called or if they are in the wrong order, an ``AssertionError`` is
raised.

**Example of an API call:**

.. code-block:: python

    # Example of a successful API call
    api_call = SuccessfulAPICall(
        '/foo/bar',
        'GET',
        response_body_deserialization={'foo': 'bar'},
    )

    # Example of an unsuccessful API call
    api_call = UnsuccessfulAPICall(
        '/foo/bar',
        'GET',
        exception=HubspotServerError('Foo is not implemented', 501),
    )


**Example of testing the deletion of a contact list:**

.. code-block:: python

    from hubspot.connection.testing import MockPortalConnection
    from hubspot.connection.testing import SuccessfulAPICall

    def test_delete_contact_list():
        list_id = 1
        url_path = '/contacts/v1/lists/{}'.format(list_id)

        api_call = SuccessfulAPICall(
            url_path,
            'DELETE',
            response_body_deserialization=None,
        )

        expected_api_calls_simulator = lambda : [api_call]

        with MockPortalConnection(expected_api_calls_simulator) as connection
            delete_list(list_id, connection)

    # Unit to be tested
    def delete_contact_list(list_id, connection):
        connection.send_delete_request('/contacts/v1/lists/{}'.format(list_id))


API
---

Authentication
++++++++++++++

.. class:: hubspot.connection.APIKey

    Representation of the HubSpot API Key

    .. attribute:: key_value

        The HubSpot API Key (`hapikey`)

.. class:: hubspot.connection.OAuthKey

    Representation of the HubSpot OAuth Key

    .. attribute:: key_value

        The HubSpot OAuth Key (`access_token`)

Connection
++++++++++

.. automodule:: hubspot.connection


Exceptions
++++++++++

.. automodule:: hubspot.connection.exc


Testing utilities
+++++++++++++++++

.. automodule:: hubspot.connection.testing

.. autoclass:: hubspot.connection.testing.APICall

    .. attribute:: url_path

        A :class:`basestring` representing the complete URL to the request

    .. attribute:: http_method

        A :class:`basestring` representing the HTTP Method to the request

    .. attribute:: query_string_args

        A :class:`dict` representing the query string args

    .. attribute:: request_body_deserialization

        A representation of the request's body

.. class:: hubspot.connection.testing.SuccessfulAPICall

    :base: :class:`APICall`

    .. attribute:: response_body_deserialization

        A represention of the response's body

.. class:: hubspot.connection.testing.UnsuccessfulAPICall

    :base: :class:`APICall`

    .. attribute:: exception

        An :class:`exception` representing the raised Exception

Support
-------

For questions directly related to *hubspot-connection*, please use our
`2degrees-floss mailing list <http://groups.google.com/group/2degrees-floss/>`_.

Please go to `our development site at GitHub
<https://github.com/2degrees/hubspot-connection/>`_ to get the
latest code, create pull requests and raise `issues
<https://github.com/2degrees/hubspot-connection/issues/>`_.


Changelog
---------

.. include:: changelog.rst

