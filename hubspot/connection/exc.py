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


class HubspotException(Exception):
    """The base HubSpot error."""
    pass


class HubspotUnsupportedResponseError(HubspotException):
    pass


class HubspotClientError(HubspotException):
    """
    HubSpot deemed the request invalid. This represents an HTTP response code
    of 40X, except 401

    :param unicode request_id:
    :param unicode error_message: The error message returned by HubSpot
    :param dict optional error_data: The response data returned by HubSpot
    :param int optional http_status_code:

    """
    def __init__(self, error_message, request_id, error_data=None, http_status_code=None):
        if error_data and 'failureMessages' in error_data:
            msg = u'{0} ({1!s})'.format(error_message, error_data['failureMessages'])
        else:
            msg = error_message
        super(HubspotClientError, self).__init__(msg)

        self.http_status_code = http_status_code
        self.error_message = error_message
        self.request_id = request_id
        self.error_data = error_data


class HubspotAuthenticationError(HubspotClientError):
    """
    HubSpot rejected your authentication key. This represents an HTTP
    response code of 401.

    """
    pass


class HubspotServerError(HubspotException):
    """
    HubSpot failed to process the request due to a problem at their end. This
    represents an HTTP response code of 50X.

    :param int http_status_code:

    """
    def __init__(self, msg, http_status_code):
        super(HubspotServerError, self).__init__(msg)

        self.http_status_code = http_status_code

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{} {}'.format(self.http_status_code, self.message)

