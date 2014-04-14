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

from re import escape as escape_regexp
from uuid import uuid4 as get_uuid4

from nose.tools import assert_raises_regexp


def get_uuid4_str():
    uuid4 = get_uuid4()
    return str(uuid4)


def assert_raises_substring(
    exception_class,
    exception_message_substring,
    *args,
    **kwargs
    ):
    exception_message_substring = escape_regexp(exception_message_substring)
    exception_message_regexp = '^.*{}.*$'.format(exception_message_substring)
    return assert_raises_regexp(
        exception_class,
        exception_message_regexp,
        *args,
        **kwargs
        )
