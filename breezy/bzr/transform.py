# Copyright (C) 2006-2011 Canonical Ltd
# Copyright (C) 2020 Breezy Developers
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

from __future__ import absolute_import

from .. import (
    errors,
    osutils,
    ui,
    )

from ..i18n import gettext
from ..mutabletree import MutableTree
from ..transform import (
    TreeTransform,
    _FileMover,
    _TransformResults,
    DiskTreeTransform,
    joinpath,
    FinalPaths,
    )
from . import inventory


class InventoryTreeTransform(TreeTransform):
    """Tree transform for Bazaar trees."""

    def apply(self, no_conflicts=False, precomputed_delta=None, _mover=None):
        """Apply all changes to the inventory and filesystem.

        If filesystem or inventory conflicts are present, MalformedTransform
        will be thrown.

        If apply succeeds, finalize is not necessary.

        :param no_conflicts: if True, the caller guarantees there are no
            conflicts, so no check is made.
        :param precomputed_delta: An inventory delta to use instead of
            calculating one.
        :param _mover: Supply an alternate FileMover, for testing
        """
        for hook in MutableTree.hooks['pre_transform']:
            hook(self._tree, self)
        if not no_conflicts:
            self._check_malformed()
        with ui.ui_factory.nested_progress_bar() as child_pb:
            if precomputed_delta is None:
                child_pb.update(gettext('Apply phase'), 0, 2)
                inventory_delta = self._generate_inventory_delta()
                offset = 1
            else:
                inventory_delta = precomputed_delta
                offset = 0
            if _mover is None:
                mover = _FileMover()
            else:
                mover = _mover
            try:
                child_pb.update(gettext('Apply phase'), 0 + offset, 2 + offset)
                self._apply_removals(mover)
                child_pb.update(gettext('Apply phase'), 1 + offset, 2 + offset)
                modified_paths = self._apply_insertions(mover)
            except BaseException:
                mover.rollback()
                raise
            else:
                mover.apply_deletions()
        if self.final_file_id(self.root) is None:
            inventory_delta = [e for e in inventory_delta if e[0] != '']
        self._tree.apply_inventory_delta(inventory_delta)
        self._apply_observed_sha1s()
        self._done = True
        self.finalize()
        return _TransformResults(modified_paths, self.rename_count)

    def _inventory_altered(self):
        """Determine which trans_ids need new Inventory entries.

        An new entry is needed when anything that would be reflected by an
        inventory entry changes, including file name, file_id, parent file_id,
        file kind, and the execute bit.

        Some care is taken to return entries with real changes, not cases
        where the value is deleted and then restored to its original value,
        but some actually unchanged values may be returned.

        :returns: A list of (path, trans_id) for all items requiring an
            inventory change. Ordered by path.
        """
        changed_ids = set()
        # Find entries whose file_ids are new (or changed).
        new_file_id = set(t for t in self._new_id
                          if self._new_id[t] != self.tree_file_id(t))
        for id_set in [self._new_name, self._new_parent, new_file_id,
                       self._new_executability]:
            changed_ids.update(id_set)
        # removing implies a kind change
        changed_kind = set(self._removed_contents)
        # so does adding
        changed_kind.intersection_update(self._new_contents)
        # Ignore entries that are already known to have changed.
        changed_kind.difference_update(changed_ids)
        #  to keep only the truly changed ones
        changed_kind = (t for t in changed_kind
                        if self.tree_kind(t) != self.final_kind(t))
        # all kind changes will alter the inventory
        changed_ids.update(changed_kind)
        # To find entries with changed parent_ids, find parents which existed,
        # but changed file_id.
        # Now add all their children to the set.
        for parent_trans_id in new_file_id:
            changed_ids.update(self.iter_tree_children(parent_trans_id))
        return sorted(FinalPaths(self).get_paths(changed_ids))

    def _generate_inventory_delta(self):
        """Generate an inventory delta for the current transform."""
        inventory_delta = []
        new_paths = self._inventory_altered()
        total_entries = len(new_paths) + len(self._removed_id)
        with ui.ui_factory.nested_progress_bar() as child_pb:
            for num, trans_id in enumerate(self._removed_id):
                if (num % 10) == 0:
                    child_pb.update(gettext('removing file'),
                                    num, total_entries)
                if trans_id == self._new_root:
                    file_id = self._tree.path2id('')
                else:
                    file_id = self.tree_file_id(trans_id)
                # File-id isn't really being deleted, just moved
                if file_id in self._r_new_id:
                    continue
                path = self._tree_id_paths[trans_id]
                inventory_delta.append((path, None, file_id, None))
            new_path_file_ids = dict((t, self.final_file_id(t)) for p, t in
                                     new_paths)
            for num, (path, trans_id) in enumerate(new_paths):
                if (num % 10) == 0:
                    child_pb.update(gettext('adding file'),
                                    num + len(self._removed_id), total_entries)
                file_id = new_path_file_ids[trans_id]
                if file_id is None:
                    continue
                kind = self.final_kind(trans_id)
                if kind is None:
                    kind = self._tree.stored_kind(self._tree.id2path(file_id))
                parent_trans_id = self.final_parent(trans_id)
                parent_file_id = new_path_file_ids.get(parent_trans_id)
                if parent_file_id is None:
                    parent_file_id = self.final_file_id(parent_trans_id)
                if trans_id in self._new_reference_revision:
                    new_entry = inventory.TreeReference(
                        file_id,
                        self._new_name[trans_id],
                        self.final_file_id(self._new_parent[trans_id]),
                        None, self._new_reference_revision[trans_id])
                else:
                    new_entry = inventory.make_entry(kind,
                                                     self.final_name(trans_id),
                                                     parent_file_id, file_id)
                try:
                    old_path = self._tree.id2path(new_entry.file_id)
                except errors.NoSuchId:
                    old_path = None
                new_executability = self._new_executability.get(trans_id)
                if new_executability is not None:
                    new_entry.executable = new_executability
                inventory_delta.append(
                    (old_path, path, new_entry.file_id, new_entry))
        return inventory_delta


class TransformPreview(InventoryTreeTransform):
    """A TreeTransform for generating preview trees.

    Unlike TreeTransform, this version works when the input tree is a
    RevisionTree, rather than a WorkingTree.  As a result, it tends to ignore
    unversioned files in the input tree.
    """

    def __init__(self, tree, pb=None, case_sensitive=True):
        tree.lock_read()
        limbodir = osutils.mkdtemp(prefix='bzr-limbo-')
        DiskTreeTransform.__init__(self, tree, limbodir, pb, case_sensitive)

    def canonical_path(self, path):
        return path

    def tree_kind(self, trans_id):
        path = self._tree_id_paths.get(trans_id)
        if path is None:
            return None
        kind = self._tree.path_content_summary(path)[0]
        if kind == 'missing':
            kind = None
        return kind

    def _set_mode(self, trans_id, mode_id, typefunc):
        """Set the mode of new file contents.
        The mode_id is the existing file to get the mode from (often the same
        as trans_id).  The operation is only performed if there's a mode match
        according to typefunc.
        """
        # is it ok to ignore this?  probably
        pass

    def iter_tree_children(self, parent_id):
        """Iterate through the entry's tree children, if any"""
        try:
            path = self._tree_id_paths[parent_id]
        except KeyError:
            return
        try:
            entry = next(self._tree.iter_entries_by_dir(
                specific_files=[path]))[1]
        except StopIteration:
            return
        children = getattr(entry, 'children', {})
        for child in children:
            childpath = joinpath(path, child)
            yield self.trans_id_tree_path(childpath)

    def new_orphan(self, trans_id, parent_id):
        raise NotImplementedError(self.new_orphan)
