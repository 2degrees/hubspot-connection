Hubspot connection for API clients
**********************************

:Latest release: |release|
:Download: `<http://pypi.python.org/pypi/hubspot-connection>`_
:Development: `<https://github.com/2degrees/hubspot-connection>`_
:Author: `2degrees Limited <http://dev.2degreesnetwork.com/>`_

This is a helper for creating Hubspot API clients, :mod:`hubspot.connection` will
take care of connecting and authenticating to hubspot.

.. toctree::
    :maxdepth: 2

    changelog

Tutorial
--------

Authentication
++++++++++++++

`Hubspot oauth overview <https://developers.hubspot.com/auth/oauth_overview>`_

Hubspot provides two ways of authentication (Oauth and API Key), this module
only supports API Key.

In order to provide authentication to :mod:`hubspot.connection` you need to
create an instance of :class:`hubspot.connection.APIKey`, which just requires the Hubspot account
key. This will be passed as first argument to :class:`~hubspot.connection.PortalConnection`.

Example:
^^^^^^^^

.. code-block:: python

    authentication_key = APIKey('HUBSPOT-ACCOUNT-KEY')


How to make requests to Hubspot
+++++++++++++++++++++++++++++++

The package uses `requests <http://docs.python-requests.org/en/latest/>`_ to make
the requests, using a configured :meth:`requests.Session` which is configured for a
fixed number of max retries and a user agent, so there is not need to configure
:class:`~hubspot.connection.PortalConnection`.

.. autodata:: hubspot.connection._HTTP_CONNECTION_MAX_RETRIES

.. autodata:: hubspot.connection._USER_AGENT

With this package you can easily create new hubspot API clients, by using
:class:`~hubspot.connection.PortalConnection` instance to send the requests,
only needing to know the endpoint and arguments needed by hubspot.


Example:
^^^^^^^^

.. code-block:: python

    from hubspot.connection import APIKey
    from hubspot.connection import PortalConnection

    _ACCOUNT_KEY = 'HUBSPOT-ACCOUNT-KEY'
    _AUTHENTICATION_KEY = APIKey(_ACCOUNT_KEY)

    with PortalConnection(_AUTHENTICATION_KEY, 'client') as connection:
        contacts_data = connection.send_get_request('/contacts/v1/lists/all/contacts/all')
        for contact in contacts_data.get('contacts'):
            print contact

This will return the ``json`` for each contact in the first page of the
get all contacts Hubspot endpoint.

Not only can you issue GET requests :meth:`~hubspot.connection.PortalConnection.send_get_request` but also, PUT :func:`~hubspot.connection.PortalConnection.send_put_request`, DELETE :func:`~hubspot.connection.PortalConnection.send_delete_request` and POST :func:`~hubspot.connection.PortalConnection.send_post_request`.

A good example of a package using :mod:`hubspot.connection`` can be seen
`here <https://github.com/2degrees/hubspot-contacts>`_.

Error Handling
++++++++++++++

:mod:`hubspot.connection` will make sure to alert you if the request failed for some reasons, here are the possible exceptions you might find while using :mod:`hubspot.connection`:

- Hubspot authentication error (:class:`~hubspot.connection.exc.HubspotAuthenticationError`)
- Hubspot client error (:class:`~hubspot.connection.exc.HubspotClientError`)
- Hubspot server error (:class:`~hubspot.connection.exc.HubspotServerError`)
- Unsupported response from hubspot (:class:`~hubspot.connection.exc.HubspotUnsupportedResponseError`)


Testing
-------

To aid in testing, :mod:`hubspot.connection` comes bundled with
:class:`~hubspot.connection.testing.MockPortalConnection` which aids in testing
Husbpot API Clients.

MockPortalConnection
++++++++++++++++++++

It receives a callable with the expected mock api calls, to check that the
expected calls with the expected arguments were called, it also verifies
that no other calls were done or that there were insufficient API calls.


Example:
^^^^^^^^

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

Connection
++++++++++

.. automodule:: hubspot.connection


Exceptions
++++++++++

.. automodule:: hubspot.connection.exc


Testing Utils
+++++++++++++

.. autoclass:: hubspot.connection.testing.APICall

.. autoclass:: hubspot.connection.testing.SuccessfulAPICall

.. autoclass:: hubspot.connection.testing.UnsuccessfulAPICall

.. automodule:: hubspot.connection.testing


Support
-------

For general hubspot.connection support, please visit the `Github Page
<https://github.com/2degrees/hubspot-connection>`_.

For suggestions and questions about the library, please use our `2degrees-floss
mailing list <http://groups.google.com/group/2degrees-floss/>`_.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

