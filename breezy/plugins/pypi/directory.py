# Copyright (C) 2021 Breezy Developers
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""Directory lookup that uses pypi."""

from __future__ import absolute_import

from breezy.errors import BzrError
from breezy.trace import note
from breezy.urlutils import InvalidURL

import json

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:  # python < 3
    from urllib import urlopen, HTTPError


class PypiProjectWithoutRepositoryURL(InvalidURL):

    _fmt = "No repository URL set for pypi project %(name)s"

    def __init__(self, name, url=None):
        BzrError.__init__(self, name=name, url=url)


class NoSuchPypiProject(InvalidURL):

    _fmt = "No pypi project with name %(name)s"

    def __init__(self, name, url=None):
        BzrError.__init__(self, name=name, url=url)


class PypiDirectory(object):

    def look_up(self, name, url, purpose=None):
        """See DirectoryService.look_up"""
        try:
            with urlopen('https://pypi.org/pypi/%s/json' % name) as f:
                data = json.load(f)
        except HTTPError as e:
            if e.status == 404:
                raise NoSuchPypiProject(name, url=url)
            raise
        for key, value in data['info']['project_urls'].items():
            if key == 'Repository':
                note('Found repository URL %s for pypi project %s',
                     value, name)
                return value
        raise PypiProjectWithoutRepositoryURL(name, url=url)
