HubSpot connection for API clients
**********************************

:Sponsored by: `2degrees Limited <http://dev.2degreesnetwork.com/>`_
:Latest release: |release|

**hubspot-connection** provides a lightweight abstraction layer for making requests
to the Hubspot API.

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

In order to authenticate via :mod:`hubspot.connection`, the "API Key" has to be
wrapped around an instance of the :mod:`hubspot.connection.APIKey` class, which
in turn turn is passed on to :mod:`~hubspot.connection.PortalConnection`.

The same should be done for OAuth should the user want to use this
authentication method, but instead of using :mod:`hubspot.connection.APIKey`,
the user should instance :mod:`hubspot.connection.OAuth` instead.

**Example:**

.. code-block:: python

    # OAuth Key
    authentication_key = OAuthKey('HUBSPOT-OAUTH-KEY')

    # API Key
    authentication_key = APIKey('HUBSPOT-API-KEY')


How to make requests to HubSpot
+++++++++++++++++++++++++++++++

:class:`~hubspot.connection.PortalConnection` is meant to be used as a context
manager, it takes care of keeping the connection alive retrying 3 times after
errors. Note, this applies only to failed connections and
timeouts, never to requests where the server returns a response.

A good example of a library using :mod:`hubspot.connection` can be seen
`here <https://github.com/2degrees/hubspot-contacts>`_.


Testing
-------

`hubspot-connection` comes bundled with testing utilities designed to help
you test your own modules for communicating with HubSpot.

:class:`~hubspot.connection.testing.MockPortalConnection` will receive
simulators as arguments that will then be automatically (entering and exiting
the context manager) tested whether their calls were executed in the same
order as the arguments, with the same url paths, body_deserialization and
query string arguments. The number of calls received by the simulators
will also be checked so that no more and no less than the ones expected,
were called.

Simulators are callables that receive no arguments and return an iterable of
api calls (:class:`~hubspot.connection.testing.APICall`).

To mock API Calls this library has
:class:`~hubspot.connection.testing.SuccessfulAPICall`
and :class:`~hubspot.connection.testing.UnsuccessfulAPICall`, along with their
base class: :class:`~hubspot.connection.testing.APICall`.


**Example of an API Call:**

.. code-block:: python

    # Example of a successful mock API Call
    stub_api_call = SuccessfulAPICall(
        '/foo/bar',
        'GET',
        response_body_deserialization={'foo', 'bar'},
    )

    # Example of an unsuccessful mock API Call
    stub_api_call = UnsuccessfulAPICall(
        '/foo/bar',
        'GET',
        exception=HubspotServerError('Foo is not bar'),
    )


**Example of testing the deletion of a contact list:**

.. code-block:: python

    from hubspot.connection.testing import MockPortalConnection
    from hubspot.connection.testing import SuccessfulAPICall

    def test_delete_contact_list():
        url_path = '/contacts/v1/lists/1'

        api_call = SuccessfulAPICall(
            url_path,
            'DELETE',
            response_body_deserialization=None,
        )

        expected_api_calls_simulator = lambda : [api_call]

        with MockPortalConnection(expected_api_calls_simulator) as conn:
            conn.send_delete_request(url_path)


API
---

Authentication
++++++++++++++

.. class:: hubspot.connection.APIKey

    Representation of the HubSpot API Key

    .. attribute:: key_value

        The Hubspot Api Key (`hapikey`)

.. class:: hubspot.connection.OAuthKey

    Representation of the HubSpot OAuth Key

    .. attribute:: key_value

        The Hubspot OAuth Key (`access_token`)

Connection
++++++++++

.. automodule:: hubspot.connection


Exceptions
++++++++++

.. automodule:: hubspot.connection.exc


Testing Utils
+++++++++++++

.. automodule:: hubspot.connection.testing

.. autoclass:: hubspot.connection.testing.APICall

    .. attribute:: url_path

        A :class:`basestring` representing the complete url for the request

    .. attribute:: http_method

        A :class:`basestring` representing the HTTP Method for the request

    .. attribute:: query_string_args

        A :class:`dict` representing the query string args

    .. attribute:: request_body_deserialization

        A :class:`dict` representing the request's body

.. class:: hubspot.connection.testing.SuccessfulAPICall

    :base: :class:`APICall`

    .. attribute:: response_body_deserialization

        A :class:`dict` representing the response's body

.. class:: hubspot.connection.testing.UnsuccessfulAPICall

    :base: :class:`APICall`

    .. attribute:: exception

        An :class:`exception` representing the raised Exception

Support
-------

For questions directly related to *hubspot-connection*, please use our
`2degrees-floss mailing list <http://groups.google.com/group/2degrees-floss/>`_.

Please go to `our development site on GitHub
<https://github.com/2degrees/hubspot-connection/>`_ to get the
latest code, create pull requests and raise `issues
<https://github.com/2degrees/hubspot-connection/issues/>`_.


.. include:: changelog.rst


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

