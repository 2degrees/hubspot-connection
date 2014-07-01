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

    """
    def __init__(self, msg, request_id):
        super(HubspotClientError, self).__init__(msg)

        self.request_id = request_id


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

