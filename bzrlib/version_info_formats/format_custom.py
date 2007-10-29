# Copyright (C) 2007 Canonical Ltd
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""A generator which creates a C header file from the current tree info"""

from bzrlib.lazy_regex import lazy_compile
from bzrlib.version_info_formats import (
   create_date_str,
   VersionInfoBuilder,
   )


class Template(dict):
    """A simple template engine.

    >>> t = Template()
    >>> t['test'] = 'xxx'
    >>> print list(t.process('{test}'))
    ['xxx']
    >>> print list(t.process('{test} test'))
    ['xxx', ' test']
    >>> print list(t.process('test {test}'))
    ['test ', 'xxx']
    >>> print list(t.process('test {test} test'))
    ['test ', 'xxx', ' test']
    >>> print list(t.process('{test}\\\\n'))
    ['xxx', '\\n']
    >>> print list(t.process('{test}\\n'))
    ['xxx', '\\n']
    """

    _tag_re = lazy_compile('{(\w+)}')

    def process(self, tpl):
        tpl = tpl.decode('string_escape')
        pos = 0
        while True:
            match = self._tag_re.search(tpl, pos)
            if not match:
                if pos < len(tpl):
                    yield tpl[pos:]
                break
            start, end = match.span()
            if start > 0:
                yield tpl[pos:start]
            pos = end
            name = match.group(1)
            data = self.get(name, u'')
            if not isinstance(data, basestring):
                data = str(data)
            yield data


class CustomVersionInfoBuilder(VersionInfoBuilder):
    """Create a version file based on a custom template."""

    def generate(self, to_file):
        info = Template()
        info['build_date'] = create_date_str()
        info['branch_nick'] = self._branch.nick

        revision_id = self._get_revision_id()
        if revision_id is None:
            info['revno'] = 0
        else:
            info['revno'] = self._branch.revision_id_to_revno(revision_id)
            info['revision_id'] = revision_id
            rev = self._branch.repository.get_revision(revision_id)
            info['date'] = create_date_str(rev.timestamp, rev.timezone)

        if self._check:
            self._extract_file_revisions()

        if self._check:
            if self._clean:
                info['clean'] = 1
            else:
                info['clean'] = 0

        to_file.writelines(info.process(self._template))
