# Copyright (C) 2018 Jelmer Vernooij <jelmer@samba.org>
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


"""Git Memory Trees."""

from __future__ import absolute_import

from dulwich.objects import (
    Tree,
    )

from breezy import (
    lock,
    osutils,
    revision as _mod_revision,
    tree as _mod_tree,
    )
from breezy.transport.memory import MemoryTransport

from .mapping import GitFileIdMap
from .tree import MutableGitIndexTree

class GitMemoryTree(MutableGitIndexTree,_mod_tree.Tree):
    """A Git memory tree."""

    def __init__(self, branch, store, head):
        MutableGitIndexTree.__init__(self)
        self.branch = branch
        self.mapping = self.branch.repository.get_mapping()
        self.store = store
        self.index = {}
        self.head = head
        self._locks = 0
        self._lock_mode = None
        self._populate_from_branch()

    def is_control_filename(self, path):
        return False

    def _gather_kinds(self, files, kinds):
        """See MutableTree._gather_kinds.
        """
        with self.lock_tree_write():
            for pos, f in enumerate(files):
                if kinds[pos] is None:
                    stat_value = self._file_transport.stat(f)
                    kinds[pos] = osutils.file_kind_from_stat_mode(stat_value.st_mode)

    def put_file_bytes_non_atomic(self, path, bytes, file_id=None):
        """See MutableTree.put_file_bytes_non_atomic."""
        self._file_transport.put_bytes(path, bytes)

    def _populate_from_branch(self):
        """Populate the in-tree state from the branch."""
        if self.head is None:
            self._parent_ids = []
        else:
            self._parent_ids = [self.last_revision()]
        self._file_transport = MemoryTransport()
        if self.head is None:
            tree = Tree()
            self._basis_fileid_map = GitFileIdMap({}, self.mapping)
        else:
            tree_id = self.store[self.head].tree
            self._basis_fileid_map = self.mapping.get_fileid_map(
                self.store.__getitem__, tree_id)
            tree = self.store[tree_id]
        self._fileid_map = self._basis_fileid_map.copy()

        trees = [("", tree)]
        while trees:
            (path, tree) = trees.pop()
            for name, mode, sha in tree.iteritems():
                subpath = posixpath.join(path, name)
                if stat.S_ISDIR(mode):
                    self._file_transport.mkdir(subpath)
                    trees.append((subpath, sha))
                elif stat.S_ISREG(mode):
                    self._file_transport.put_bytes(subpath, self.store[sha].data)
                    self._index_add_entry(subpath, 'kind')
                else:
                    raise NotImplementedError(self._populate_from_branch)

    def lock_read(self):
        """Lock the memory tree for reading.

        This triggers population of data from the branch for its revision.
        """
        self._locks += 1
        try:
            if self._locks == 1:
                self.branch.lock_read()
                self._lock_mode = "r"
                self._populate_from_branch()
            return lock.LogicalLockResult(self.unlock)
        except:
            self._locks -= 1
            raise

    def lock_tree_write(self):
        """See MutableTree.lock_tree_write()."""
        self._locks += 1
        try:
            if self._locks == 1:
                self.branch.lock_read()
                self._lock_mode = "w"
                self._populate_from_branch()
            elif self._lock_mode == "r":
                raise errors.ReadOnlyError(self)
        except:
            self._locks -= 1
            raise
        return lock.LogicalLockResult(self.unlock)

    def lock_write(self):
        """See MutableTree.lock_write()."""
        self._locks += 1
        try:
            if self._locks == 1:
                self.branch.lock_write()
                self._lock_mode = "w"
                self._populate_from_branch()
            elif self._lock_mode == "r":
                raise errors.ReadOnlyError(self)
            return lock.LogicalLockResult(self.unlock)
        except:
            self._locks -= 1
            raise

    def unlock(self):
        """Release a lock.

        This frees all cached state when the last lock context for the tree is
        left.
        """
        if self._locks == 1:
            self._basis_tree = None
            self._parent_ids = []
            self.index = {}
            try:
                self.branch.unlock()
            finally:
                self._locks = 0
                self._lock_mode = None
        else:
            self._locks -= 1

    def _lstat(self, path):
        return self._file_transport.stat(path)

    def get_file(self, path, file_id=None):
        """See Tree.get_file."""
        return self._file_transport.get(path)

    def get_file_sha1(self, path, file_id=None, stat_value=None):
        """See Tree.get_file_sha1()."""
        stream = self._file_transport.get(path)
        return osutils.sha_file(stream)

    def get_parent_ids(self):
        """See Tree.get_parent_ids.

        This implementation returns the current cached value from
            self._parent_ids.
        """
        with self.lock_read():
            return list(self._parent_ids)

    def last_revision(self):
        """See MutableTree.last_revision."""
        with self.lock_read():
            if self.head is None:
                return _mod_revision.NULL_REVISION
            return self.branch.repository.lookup_foreign_revision_id(self.head)

    def basis_tree(self):
        """See Tree.basis_tree()."""
        return self.branch.repository.revision_tree(self.last_revision())

    def get_config_stack(self):
        return self.branch.get_config_stack()

    def _set_merges_from_parent_ids(self, rhs_parent_ids):
        if self.head is None:
            self._parent_ids = []
        else:
            self._parent_ids = [self.last_revision()]
        self._parent_ids.extend(rhs_parent_ids)
