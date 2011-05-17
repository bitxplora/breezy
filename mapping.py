# Copyright (C) 2007 Canonical Ltd
# Copyright (C) 2008-2010 Jelmer Vernooij <jelmer@samba.org>
# Copyright (C) 2008 John Carr
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

"""Converters, etc for going between Bazaar and Git ids."""

import base64
import stat

from bzrlib import (
    bencode,
    errors,
    foreign,
    trace,
    )
from bzrlib.inventory import (
    ROOT_ID,
    )
from bzrlib.foreign import (
    ForeignVcs,
    VcsMappingRegistry,
    ForeignRevision,
    )
from bzrlib.revision import (
    NULL_REVISION,
    )
from bzrlib.plugins.git.hg import (
    format_hg_metadata,
    extract_hg_metadata,
    )
from bzrlib.plugins.git.roundtrip import (
    extract_bzr_metadata,
    inject_bzr_metadata,
    BzrGitRevisionMetadata,
    deserialize_fileid_map,
    serialize_fileid_map,
    )

DEFAULT_FILE_MODE = stat.S_IFREG | 0644


def escape_file_id(file_id):
    return file_id.replace('_', '__').replace(' ', '_s')


def unescape_file_id(file_id):
    ret = []
    i = 0
    while i < len(file_id):
        if file_id[i] != '_':
            ret.append(file_id[i])
        else:
            if file_id[i+1] == '_':
                ret.append("_")
            elif file_id[i+1] == 's':
                ret.append(" ")
            else:
                raise AssertionError("unknown escape character %s" %
                    file_id[i+1])
            i += 1
        i += 1
    return "".join(ret)


def fix_person_identifier(text):
    if "<" in text and ">" in text:
        return text
    return "%s <%s>" % (text, text)


def warn_escaped(commit, num_escaped):
    trace.warning("Escaped %d XML-invalid characters in %s. Will be unable "
                  "to regenerate the SHA map.", num_escaped, commit)


def warn_unusual_mode(commit, path, mode):
    trace.mutter("Unusual file mode %o for %s in %s. Storing as revision "
                 "property. ", mode, path, commit)


class BzrGitMapping(foreign.VcsMapping):
    """Class that maps between Git and Bazaar semantics."""
    experimental = False

    BZR_FILE_IDS_FILE = None

    BZR_DUMMY_FILE = None

    def __init__(self):
        super(BzrGitMapping, self).__init__(foreign_vcs_git)

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.revid_prefix == other.revid_prefix)

    @classmethod
    def revision_id_foreign_to_bzr(cls, git_rev_id):
        """Convert a git revision id handle to a Bazaar revision id."""
        from dulwich.protocol import ZERO_SHA
        if git_rev_id == ZERO_SHA:
            return NULL_REVISION
        return "%s:%s" % (cls.revid_prefix, git_rev_id)

    @classmethod
    def revision_id_bzr_to_foreign(cls, bzr_rev_id):
        """Convert a Bazaar revision id to a git revision id handle."""
        if not bzr_rev_id.startswith("%s:" % cls.revid_prefix):
            raise errors.InvalidRevisionId(bzr_rev_id, cls)
        return bzr_rev_id[len(cls.revid_prefix)+1:], cls()

    def generate_file_id(self, path):
        # Git paths are just bytestrings
        # We must just hope they are valid UTF-8..
        if path == "":
            return ROOT_ID
        if type(path) is unicode:
            path = path.encode("utf-8")
        return escape_file_id(path)

    def is_control_file(self, path):
        return path in (self.BZR_FILE_IDS_FILE, self.BZR_DUMMY_FILE)

    def parse_file_id(self, file_id):
        if file_id == ROOT_ID:
            return ""
        return unescape_file_id(file_id)

    def revid_as_refname(self, revid):
        import urllib
        return "refs/bzr/%s" % urllib.quote(revid)

    def import_unusual_file_modes(self, rev, unusual_file_modes):
        if unusual_file_modes:
            ret = [(path, unusual_file_modes[path])
                   for path in sorted(unusual_file_modes.keys())]
            rev.properties['file-modes'] = bencode.bencode(ret)

    def export_unusual_file_modes(self, rev):
        try:
            file_modes = rev.properties['file-modes']
        except KeyError:
            return {}
        else:
            return dict([(self.generate_file_id(path), mode) for (path, mode) in bencode.bdecode(file_modes.encode("utf-8"))])

    def _generate_git_svn_metadata(self, rev, encoding):
        try:
            git_svn_id = rev.properties["git-svn-id"]
        except KeyError:
            return ""
        else:
            return "\ngit-svn-id: %s\n" % git_svn_id.encode(encoding)

    def _generate_hg_message_tail(self, rev):
        extra = {}
        renames = []
        branch = 'default'
        for name in rev.properties:
            if name == 'hg:extra:branch':
                branch = rev.properties['hg:extra:branch']
            elif name.startswith('hg:extra'):
                extra[name[len('hg:extra:'):]] = base64.b64decode(
                    rev.properties[name])
            elif name == 'hg:renames':
                renames = bencode.bdecode(base64.b64decode(
                    rev.properties['hg:renames']))
            # TODO: Export other properties as 'bzr:' extras?
        ret = format_hg_metadata(renames, branch, extra)
        assert isinstance(ret, str)
        return ret

    def _extract_git_svn_metadata(self, rev, message):
        lines = message.split("\n")
        if not (lines[-1] == "" and len(lines) >= 2 and lines[-2].startswith("git-svn-id:")):
            return message
        git_svn_id = lines[-2].split(": ", 1)[1]
        rev.properties['git-svn-id'] = git_svn_id
        (url, rev, uuid) = parse_git_svn_id(git_svn_id)
        # FIXME: Convert this to converted-from property somehow..
        ret = "\n".join(lines[:-2])
        assert isinstance(ret, str)
        return ret

    def _extract_hg_metadata(self, rev, message):
        (message, renames, branch, extra) = extract_hg_metadata(message)
        if branch is not None:
            rev.properties['hg:extra:branch'] = branch
        for name, value in extra.iteritems():
            rev.properties['hg:extra:' + name] = base64.b64encode(value)
        if renames:
            rev.properties['hg:renames'] = base64.b64encode(bencode.bencode(
                [(new, old) for (old, new) in renames.iteritems()]))
        return message

    def _extract_bzr_metadata(self, rev, message):
        (message, metadata) = extract_bzr_metadata(message)
        return message, metadata

    def _decode_commit_message(self, rev, message, encoding):
        return message.decode(encoding), BzrGitRevisionMetadata()

    def _encode_commit_message(self, rev, message, encoding):
        return message.encode(encoding)

    def export_fileid_map(self, fileid_map):
        """Export a file id map to a fileid map.

        :param fileid_map: File id map, mapping paths to file ids
        :return: A Git blob object
        """
        from dulwich.objects import Blob
        b = Blob()
        b.set_raw_chunks(serialize_fileid_map(fileid_map))
        return b

    def export_commit(self, rev, tree_sha, parent_lookup, roundtrip,
                      verifiers):
        """Turn a Bazaar revision in to a Git commit

        :param tree_sha: Tree sha for the commit
        :param parent_lookup: Function for looking up the GIT sha equiv of a
            bzr revision
        :param roundtrip: Whether to store roundtripping information.
        :param verifiers: Verifiers info
        :return dulwich.objects.Commit represent the revision:
        """
        from dulwich.objects import Commit
        commit = Commit()
        commit.tree = tree_sha
        if roundtrip:
            metadata = BzrGitRevisionMetadata()
            metadata.verifiers = verifiers
        else:
            metadata = None
        parents = []
        for p in rev.parent_ids:
            try:
                git_p = parent_lookup(p)
            except KeyError:
                git_p = None
                if metadata is not None:
                    metadata.explicit_parent_ids = rev.parent_ids
            if git_p is not None:
                assert len(git_p) == 40, "unexpected length for %r" % git_p
                parents.append(git_p)
        commit.parents = parents
        try:
            encoding = rev.properties['git-explicit-encoding']
        except KeyError:
            encoding = rev.properties.get('git-implicit-encoding', 'utf-8')
        commit.encoding = rev.properties.get('git-explicit-encoding')
        commit.committer = fix_person_identifier(rev.committer.encode(
            encoding))
        commit.author = fix_person_identifier(
            rev.get_apparent_authors()[0].encode(encoding))
        commit.commit_time = long(rev.timestamp)
        if 'author-timestamp' in rev.properties:
            commit.author_time = long(rev.properties['author-timestamp'])
        else:
            commit.author_time = commit.commit_time
        commit._commit_timezone_neg_utc = "commit-timezone-neg-utc" in rev.properties
        commit.commit_timezone = rev.timezone
        commit._author_timezone_neg_utc = "author-timezone-neg-utc" in rev.properties
        if 'author-timezone' in rev.properties:
            commit.author_timezone = int(rev.properties['author-timezone'])
        else:
            commit.author_timezone = commit.commit_timezone
        commit.message = self._encode_commit_message(rev, rev.message, 
            encoding)
        assert type(commit.message) == str
        if metadata is not None:
            try:
                mapping_registry.parse_revision_id(rev.revision_id)
            except errors.InvalidRevisionId:
                metadata.revision_id = rev.revision_id
            mapping_properties = set(
                ['author', 'author-timezone', 'author-timezone-neg-utc',
                 'commit-timezone-neg-utc', 'git-implicit-encoding',
                 'git-explicit-encoding', 'author-timestamp', 'file-modes'])
            for k, v in rev.properties.iteritems():
                if not k in mapping_properties:
                    metadata.properties[k] = v
        if self.roundtripping:
            commit.message = inject_bzr_metadata(commit.message, metadata, 
                                                 encoding)
        assert type(commit.message) == str
        return commit

    def import_fileid_map(self, blob):
        """Convert a git file id map blob.

        :param blob: Git blob object with fileid map
        :return: Dictionary mapping paths to file ids
        """
        return deserialize_fileid_map(blob.data)

    def import_commit(self, commit, lookup_parent_revid):
        """Convert a git commit to a bzr revision.

        :return: a `bzrlib.revision.Revision` object, foreign revid and a
            testament sha1
        """
        if commit is None:
            raise AssertionError("Commit object can't be None")
        rev = ForeignRevision(commit.id, self,
                self.revision_id_foreign_to_bzr(commit.id))
        rev.git_metadata = None
        def decode_using_encoding(rev, commit, encoding):
            rev.committer = str(commit.committer).decode(encoding)
            if commit.committer != commit.author:
                rev.properties['author'] = str(commit.author).decode(encoding)
            rev.message, rev.git_metadata = self._decode_commit_message(
                rev, commit.message, encoding)
        if commit.encoding is not None:
            rev.properties['git-explicit-encoding'] = commit.encoding
            decode_using_encoding(rev, commit, commit.encoding)
        else:
            for encoding in ('utf-8', 'latin1'):
                try:
                    decode_using_encoding(rev, commit, encoding)
                except UnicodeDecodeError:
                    pass
                else:
                    if encoding != 'utf-8':
                        rev.properties['git-implicit-encoding'] = encoding
                    break
        if commit.commit_time != commit.author_time:
            rev.properties['author-timestamp'] = str(commit.author_time)
        if commit.commit_timezone != commit.author_timezone:
            rev.properties['author-timezone'] = "%d" % commit.author_timezone
        if commit._author_timezone_neg_utc:
            rev.properties['author-timezone-neg-utc'] = ""
        if commit._commit_timezone_neg_utc:
            rev.properties['commit-timezone-neg-utc'] = ""
        rev.timestamp = commit.commit_time
        rev.timezone = commit.commit_timezone
        rev.parent_ids = None
        if rev.git_metadata is not None:
            md = rev.git_metadata
            roundtrip_revid = md.revision_id
            if md.explicit_parent_ids:
                rev.parent_ids = md.explicit_parent_ids
            rev.properties.update(md.properties)
            verifiers = md.verifiers
        else:
            roundtrip_revid = None
            verifiers = {}
        if rev.parent_ids is None:
            rev.parent_ids = tuple([lookup_parent_revid(p) for p in commit.parents])
        return rev, roundtrip_revid, verifiers

    def get_fileid_map(self, lookup_object, tree_sha):
        """Obtain a fileid map for a particular tree.

        :param lookup_object: Function for looking up an object
        :param tree_sha: SHA of the root tree
        :return: GitFileIdMap instance
        """
        try:
            file_id_map_sha = lookup_object(tree_sha)[self.BZR_FILE_IDS_FILE][1]
        except KeyError:
            file_ids = {}
        else:
            file_ids = self.import_fileid_map(lookup_object(file_id_map_sha))
        return GitFileIdMap(file_ids, self)


class BzrGitMappingv1(BzrGitMapping):
    revid_prefix = 'git-v1'
    experimental = False

    def __str__(self):
        return self.revid_prefix


class BzrGitMappingExperimental(BzrGitMappingv1):
    revid_prefix = 'git-experimental'
    experimental = True
    roundtripping = True

    BZR_FILE_IDS_FILE = '.bzrfileids'

    BZR_DUMMY_FILE = '.bzrdummy'

    def _decode_commit_message(self, rev, message, encoding):
        message = self._extract_hg_metadata(rev, message)
        message = self._extract_git_svn_metadata(rev, message)
        message, metadata = self._extract_bzr_metadata(rev, message)
        return message.decode(encoding), metadata

    def _encode_commit_message(self, rev, message, encoding):
        ret = message.encode(encoding)
        ret += self._generate_hg_message_tail(rev)
        ret += self._generate_git_svn_metadata(rev, encoding)
        return ret

    def import_commit(self, commit, lookup_parent_revid):
        rev, roundtrip_revid, verifiers = super(BzrGitMappingExperimental, self).import_commit(commit, lookup_parent_revid)
        rev.properties['converted_revision'] = "git %s\n" % commit.id
        return rev, roundtrip_revid, verifiers


class GitMappingRegistry(VcsMappingRegistry):
    """Registry with available git mappings."""

    def revision_id_bzr_to_foreign(self, bzr_revid):
        if bzr_revid == NULL_REVISION:
            from dulwich.protocol import ZERO_SHA
            return ZERO_SHA, None
        if not bzr_revid.startswith("git-"):
            raise errors.InvalidRevisionId(bzr_revid, None)
        (mapping_version, git_sha) = bzr_revid.split(":", 1)
        mapping = self.get(mapping_version)
        return mapping.revision_id_bzr_to_foreign(bzr_revid)

    parse_revision_id = revision_id_bzr_to_foreign


mapping_registry = GitMappingRegistry()
mapping_registry.register_lazy('git-v1', "bzrlib.plugins.git.mapping",
    "BzrGitMappingv1")
mapping_registry.register_lazy('git-experimental',
    "bzrlib.plugins.git.mapping", "BzrGitMappingExperimental")
mapping_registry.set_default('git-v1')


class ForeignGit(ForeignVcs):
    """The Git Stupid Content Tracker"""

    @property
    def branch_format(self):
        from bzrlib.plugins.git.branch import GitBranchFormat
        return GitBranchFormat()

    @property
    def repository_format(self):
        from bzrlib.plugins.git.repository import GitRepositoryFormat
        return GitRepositoryFormat()

    def __init__(self):
        super(ForeignGit, self).__init__(mapping_registry)
        self.abbreviation = "git"

    @classmethod
    def serialize_foreign_revid(self, foreign_revid):
        return foreign_revid

    @classmethod
    def show_foreign_revid(cls, foreign_revid):
        return { "git commit": foreign_revid }


foreign_vcs_git = ForeignGit()
default_mapping = mapping_registry.get_default()()


def symlink_to_blob(entry):
    from dulwich.objects import Blob
    blob = Blob()
    symlink_target = entry.symlink_target
    if type(symlink_target) == unicode:
        symlink_target = symlink_target.encode('utf-8')
    blob.data = symlink_target
    return blob


def mode_is_executable(mode):
    """Check if mode should be considered executable."""
    return bool(mode & 0111)


def mode_kind(mode):
    """Determine the Bazaar inventory kind based on Unix file mode."""
    entry_kind = (mode & 0700000) / 0100000
    if entry_kind == 0:
        return 'directory'
    elif entry_kind == 1:
        file_kind = (mode & 070000) / 010000
        if file_kind == 0:
            return 'file'
        elif file_kind == 2:
            return 'symlink'
        elif file_kind == 6:
            return 'tree-reference'
        else:
            raise AssertionError(
                "Unknown file kind %d, perms=%o." % (file_kind, mode,))
    else:
        raise AssertionError(
            "Unknown kind, perms=%r." % (mode,))


def object_mode(kind, executable):
    if kind == 'directory':
        return stat.S_IFDIR
    elif kind == 'symlink':
        mode = stat.S_IFLNK
        if executable:
            mode |= 0111
        return mode
    elif kind == 'file':
        mode = stat.S_IFREG | 0644
        if executable:
            mode |= 0111
        return mode
    elif kind == 'tree-reference':
        from dulwich.objects import S_IFGITLINK
        return S_IFGITLINK
    else:
        raise AssertionError


def entry_mode(entry):
    """Determine the git file mode for an inventory entry."""
    return object_mode(entry.kind, entry.executable)


def directory_to_tree(entry, lookup_ie_sha1, unusual_modes, empty_file_name):
    """Create a Git Tree object from a Bazaar directory.

    :param entry: Inventory entry
    :param lookup_ie_sha1: Lookup the Git SHA1 for a inventory entry
    :param unusual_modes: Dictionary with unusual file modes by file ids
    :param empty_file_name: Name to use for dummy files in empty directories,
        None to ignore empty directories.
    """
    from dulwich.objects import Blob, Tree
    tree = Tree()
    for name, value in entry.children.iteritems():
        ie = entry.children[name]
        try:
            mode = unusual_modes[ie.file_id]
        except KeyError:
            mode = entry_mode(ie)
        hexsha = lookup_ie_sha1(ie)
        if hexsha is not None:
            tree.add(name.encode("utf-8"), mode, hexsha)
    if entry.parent_id is not None and len(tree) == 0:
        # Only the root can be an empty tree
        if empty_file_name is not None:
            tree.add(empty_file_name, stat.S_IFREG | 0644, Blob().id)
        else:
            return None
    return tree


def extract_unusual_modes(rev):
    try:
        foreign_revid, mapping = mapping_registry.parse_revision_id(
            rev.revision_id)
    except errors.InvalidRevisionId:
        return {}
    else:
        return mapping.export_unusual_file_modes(rev)


def parse_git_svn_id(text):
    (head, uuid) = text.rsplit(" ", 1)
    (full_url, rev) = head.rsplit("@", 1)
    return (full_url, int(rev), uuid)


class GitFileIdMap(object):

    def __init__(self, file_ids, mapping):
        self.file_ids = file_ids
        self.paths = None
        self.mapping = mapping

    def set_file_id(self, path, file_id):
        assert type(path) is str
        assert type(file_id) is str
        self.file_ids[path] = file_id

    def lookup_file_id(self, path):
        assert type(path) is str
        try:
            file_id = self.file_ids[path]
        except KeyError:
            file_id = self.mapping.generate_file_id(path)
        assert type(file_id) is str
        return file_id

    def lookup_path(self, file_id):
        if self.paths is None:
            self.paths = {}
            for k, v in self.file_ids.iteritems():
                self.paths[v] = k
        try:
            path = self.paths[file_id]
        except KeyError:
            return self.mapping.parse_file_id(file_id)
        else:
            assert type(path) is str
            return path

    def copy(self):
        return self.__class__(dict(self.file_ids), self.mapping)
