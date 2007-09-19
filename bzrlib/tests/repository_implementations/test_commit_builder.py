# Copyright (C) 2006 Canonical Ltd
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

"""Tests for repository commit builder."""

import errno
import os
import sys

from bzrlib import (
    errors,
    inventory,
    osutils,
    repository,
    tests,
    )
from bzrlib.tests.repository_implementations import test_repository


class TestCommitBuilder(test_repository.TestCaseWithRepository):

    def test_get_commit_builder(self):
        branch = self.make_branch('.')
        branch.repository.lock_write()
        builder = branch.repository.get_commit_builder(
            branch, [], branch.get_config())
        self.assertIsInstance(builder, repository.CommitBuilder)
        self.assertTrue(builder.random_revid)
        branch.repository.commit_write_group()
        branch.repository.unlock()

    def record_root(self, builder, tree):
        if builder.record_root_entry is True:
            tree.lock_read()
            try:
                ie = tree.inventory.root
            finally:
                tree.unlock()
            parent_tree = tree.branch.repository.revision_tree(None)
            parent_invs = []
            builder.record_entry_contents(ie, parent_invs, '', tree)

    def test_finish_inventory(self):
        tree = self.make_branch_and_tree(".")
        tree.lock_write()
        try:
            builder = tree.branch.get_commit_builder([])
            self.record_root(builder, tree)
            builder.finish_inventory()
            tree.branch.repository.commit_write_group()
        finally:
            tree.unlock()

    def test_abort(self):
        tree = self.make_branch_and_tree(".")
        tree.lock_write()
        try:
            builder = tree.branch.get_commit_builder([])
            self.record_root(builder, tree)
            builder.finish_inventory()
            builder.abort()
        finally:
            tree.unlock()

    def test_commit_message(self):
        tree = self.make_branch_and_tree(".")
        tree.lock_write()
        try:
            builder = tree.branch.get_commit_builder([])
            self.record_root(builder, tree)
            builder.finish_inventory()
            rev_id = builder.commit('foo bar blah')
        finally:
            tree.unlock()
        rev = tree.branch.repository.get_revision(rev_id)
        self.assertEqual('foo bar blah', rev.message)

    def test_commit_with_revision_id(self):
        tree = self.make_branch_and_tree(".")
        tree.lock_write()
        try:
            # use a unicode revision id to test more corner cases.
            # The repository layer is meant to handle this.
            revision_id = u'\xc8abc'.encode('utf8')
            try:
                try:
                    builder = tree.branch.get_commit_builder([],
                        revision_id=revision_id)
                except errors.NonAsciiRevisionId:
                    revision_id = 'abc'
                    builder = tree.branch.get_commit_builder([],
                        revision_id=revision_id)
            except errors.CannotSetRevisionId:
                # This format doesn't support supplied revision ids
                return
            self.assertFalse(builder.random_revid)
            self.record_root(builder, tree)
            builder.finish_inventory()
            self.assertEqual(revision_id, builder.commit('foo bar'))
        finally:
            tree.unlock()
        self.assertTrue(tree.branch.repository.has_revision(revision_id))
        # the revision id must be set on the inventory when saving it. This
        # does not precisely test that - a repository that wants to can add it
        # on deserialisation, but thats all the current contract guarantees
        # anyway.
        self.assertEqual(revision_id,
            tree.branch.repository.get_inventory(revision_id).revision_id)

    def test_commit_without_root(self):
        """This should cause a deprecation warning, not an assertion failure"""
        tree = self.make_branch_and_tree(".")
        tree.lock_write()
        try:
            if tree.branch.repository.supports_rich_root():
                raise tests.TestSkipped('Format requires root')
            self.build_tree(['foo'])
            tree.add('foo', 'foo-id')
            entry = tree.inventory['foo-id']
            builder = tree.branch.get_commit_builder([])
            self.callDeprecated(['Root entry should be supplied to'
                ' record_entry_contents, as of bzr 0.10.'],
                builder.record_entry_contents, entry, [], 'foo', tree)
            builder.finish_inventory()
            rev_id = builder.commit('foo bar')
        finally:
            tree.unlock()

    def test_commit(self):
        tree = self.make_branch_and_tree(".")
        tree.lock_write()
        try:
            builder = tree.branch.get_commit_builder([])
            self.record_root(builder, tree)
            builder.finish_inventory()
            rev_id = builder.commit('foo bar')
        finally:
            tree.unlock()
        self.assertNotEqual(None, rev_id)
        self.assertTrue(tree.branch.repository.has_revision(rev_id))
        # the revision id must be set on the inventory when saving it. This does not
        # precisely test that - a repository that wants to can add it on deserialisation,
        # but thats all the current contract guarantees anyway.
        self.assertEqual(rev_id, tree.branch.repository.get_inventory(rev_id).revision_id)

    def test_revision_tree(self):
        tree = self.make_branch_and_tree(".")
        tree.lock_write()
        try:
            builder = tree.branch.get_commit_builder([])
            self.record_root(builder, tree)
            builder.finish_inventory()
            rev_id = builder.commit('foo bar')
        finally:
            tree.unlock()
        rev_tree = builder.revision_tree()
        # Just a couple simple tests to ensure that it actually follows
        # the RevisionTree api.
        self.assertEqual(rev_id, rev_tree.get_revision_id())
        self.assertEqual([], rev_tree.get_parent_ids())

    def test_root_entry_has_revision(self):
        # test the root revision created and put in the basis
        # has the right rev id.
        tree = self.make_branch_and_tree('.')
        rev_id = tree.commit('message')
        basis_tree = tree.basis_tree()
        basis_tree.lock_read()
        self.addCleanup(basis_tree.unlock)
        self.assertEqual(rev_id, basis_tree.inventory.root.revision)

    def _get_revtrees(self, tree, revision_ids):
        trees = list(tree.branch.repository.revision_trees(revision_ids))
        for tree in trees:
            tree.lock_read()
            self.addCleanup(tree.unlock)
        return trees

    def test_last_modified_revision_after_commit_root_unchanged(self):
        # commiting without changing the root does not change the 
        # last modified except on non-rich-root-repositories.
        tree = self.make_branch_and_tree('.')
        rev1 = tree.commit('')
        rev2 = tree.commit('')
        tree1, tree2 = self._get_revtrees(tree, [rev1, rev2])
        self.assertEqual(rev1, tree1.inventory.root.revision)
        if tree.branch.repository.supports_rich_root():
            self.assertEqual(rev1, tree2.inventory.root.revision)
        else:
            self.assertEqual(rev2, tree2.inventory.root.revision)

    def _add_commit_check_unchanged(self, tree, name):
        tree.add([name], [name + 'id'])
        rev1 = tree.commit('')
        rev2 = tree.commit('')
        tree1, tree2 = self._get_revtrees(tree, [rev1, rev2])
        self.assertEqual(rev1, tree1.inventory[name + 'id'].revision)
        self.assertEqual(rev1, tree2.inventory[name + 'id'].revision)
        self.assertFileAncestry([rev1], tree, name)

    def test_last_modified_revision_after_commit_dir_unchanged(self):
        # committing without changing a dir does not change the last modified.
        tree = self.make_branch_and_tree('.')
        self.build_tree(['dir/'])
        self._add_commit_check_unchanged(tree, 'dir')

    def test_last_modified_revision_after_commit_dir_contents_unchanged(self):
        # committing without changing a dir does not change the last modified
        # of the dir even the dirs contents are changed.
        tree = self.make_branch_and_tree('.')
        self.build_tree(['dir/'])
        tree.add(['dir'], ['dirid'])
        rev1 = tree.commit('')
        self.build_tree(['dir/content'])
        tree.add(['dir/content'], ['contentid'])
        rev2 = tree.commit('')
        tree1, tree2 = self._get_revtrees(tree, [rev1, rev2])
        self.assertEqual(rev1, tree1.inventory['dirid'].revision)
        self.assertEqual(rev1, tree2.inventory['dirid'].revision)
        self.assertFileAncestry([rev1], tree, 'dir')

    def test_last_modified_revision_after_commit_file_unchanged(self):
        # committing without changing a file does not change the last modified.
        tree = self.make_branch_and_tree('.')
        self.build_tree(['file'])
        self._add_commit_check_unchanged(tree, 'file')

    def test_last_modified_revision_after_commit_link_unchanged(self):
        # committing without changing a link does not change the last modified.
        self.requireFeature(tests.SymlinkFeature)
        tree = self.make_branch_and_tree('.')
        os.symlink('target', 'link')
        self._add_commit_check_unchanged(tree, 'link')

    def _add_commit_renamed_check_changed(self, tree, name):
        def rename():
            tree.rename_one(name, 'new_' + name)
        self._add_commit_change_check_changed(tree, name, rename)

    def test_last_modified_revision_after_rename_dir_changes(self):
        # renaming a dir changes the last modified.
        tree = self.make_branch_and_tree('.')
        self.build_tree(['dir/'])
        self._add_commit_renamed_check_changed(tree, 'dir')

    def test_last_modified_revision_after_rename_file_changes(self):
        # renaming a file changes the last modified.
        tree = self.make_branch_and_tree('.')
        self.build_tree(['file'])
        self._add_commit_renamed_check_changed(tree, 'file')

    def test_last_modified_revision_after_rename_link_changes(self):
        # renaming a link changes the last modified.
        self.requireFeature(tests.SymlinkFeature)
        tree = self.make_branch_and_tree('.')
        os.symlink('target', 'link')
        self._add_commit_renamed_check_changed(tree, 'link')

    def _add_commit_reparent_check_changed(self, tree, name):
        self.build_tree(['newparent/'])
        tree.add(['newparent'])
        def reparent():
            tree.rename_one(name, 'newparent/new_' + name)
        self._add_commit_change_check_changed(tree, name, reparent)

    def test_last_modified_revision_after_reparent_dir_changes(self):
        # reparenting a dir changes the last modified.
        tree = self.make_branch_and_tree('.')
        self.build_tree(['dir/'])
        self._add_commit_reparent_check_changed(tree, 'dir')

    def test_last_modified_revision_after_reparent_file_changes(self):
        # reparenting a file changes the last modified.
        tree = self.make_branch_and_tree('.')
        self.build_tree(['file'])
        self._add_commit_reparent_check_changed(tree, 'file')

    def test_last_modified_revision_after_reparent_link_changes(self):
        # reparenting a link changes the last modified.
        self.requireFeature(tests.SymlinkFeature)
        tree = self.make_branch_and_tree('.')
        os.symlink('target', 'link')
        self._add_commit_reparent_check_changed(tree, 'link')

    def _add_commit_change_check_changed(self, tree, name, changer):
        tree.add([name], [name + 'id'])
        rev1 = tree.commit('')
        changer()
        rev2 = tree.commit('')
        tree1, tree2 = self._get_revtrees(tree, [rev1, rev2])
        self.assertEqual(rev1, tree1.inventory[name + 'id'].revision)
        self.assertEqual(rev2, tree2.inventory[name + 'id'].revision)
        self.assertFileAncestry([rev1, rev2], tree, name)

    def assertFileAncestry(self, ancestry, tree, name, alt_ancestry=None):
        # all the changes that have occured should be in the ancestry
        # (closest to a public per-file graph API we have today)
        tree.lock_read()
        self.addCleanup(tree.unlock)
        vw = tree.branch.repository.weave_store.get_weave(name + 'id',
            tree.branch.repository.get_transaction())
        result = vw.get_ancestry([ancestry[-1]])
        if alt_ancestry is None:
            self.assertEqual(ancestry, result)
        else:
            self.assertSubset([tuple(result)],
                [tuple(ancestry), tuple(alt_ancestry)])

    def test_last_modified_revision_after_content_file_changes(self):
        # altering a file changes the last modified.
        tree = self.make_branch_and_tree('.')
        self.build_tree(['file'])
        def change_file():
            tree.put_file_bytes_non_atomic('fileid', 'new content')
        self._add_commit_change_check_changed(tree, 'file', change_file)

    def test_last_modified_revision_after_content_link_changes(self):
        # changing a link changes the last modified.
        self.requireFeature(tests.SymlinkFeature)
        tree = self.make_branch_and_tree('.')
        os.symlink('target', 'link')
        def change_link():
            os.unlink('link')
            os.symlink('newtarget', 'link')
        self._add_commit_change_check_changed(tree, 'link', change_link)

    def _commit_sprout(self, tree, name):
        tree.add([name], [name + 'id'])
        rev_id = tree.commit('')
        return rev_id, tree.bzrdir.sprout('t2').open_workingtree()

    def _rename_in_tree(self, tree, name):
        tree.rename_one(name, 'new_' + name)
        return tree.commit('')

    def _commit_sprout_rename_merge(self, tree1, name):
        rev1, tree2 = self._commit_sprout(tree1, name)
        # change both sides equally
        rev2 = self._rename_in_tree(tree1, name)
        rev3 = self._rename_in_tree(tree2, name)
        tree1.merge_from_branch(tree2.branch)
        rev4 = tree1.commit('')
        tree3, = self._get_revtrees(tree1, [rev4])
        self.assertEqual(rev4, tree3.inventory[name + 'id'].revision)
        self.assertFileAncestry([rev1, rev2, rev3, rev4], tree1, name,
            [rev1, rev3, rev2, rev4])

    def test_last_modified_revision_after_merge_dir_changes(self):
        # merge a dir changes the last modified.
        tree1 = self.make_branch_and_tree('t1')
        self.build_tree(['t1/dir/'])
        self._commit_sprout_rename_merge(tree1, 'dir')

    def test_last_modified_revision_after_merge_file_changes(self):
        # merge a file changes the last modified.
        tree1 = self.make_branch_and_tree('t1')
        self.build_tree(['t1/file'])
        self._commit_sprout_rename_merge(tree1, 'file')

    def test_last_modified_revision_after_merge_link_changes(self):
        # merge a link changes the last modified.
        self.requireFeature(tests.SymlinkFeature)
        tree1 = self.make_branch_and_tree('t1')
        os.symlink('target', 't1/link')
        self._commit_sprout_rename_merge(tree1, 'link')

    def _commit_sprout_rename_merge_converged(self, tree1, name):
        rev1, tree2 = self._commit_sprout(tree1, name)
        # change on the other side to merge back
        rev2 = self._rename_in_tree(tree2, name)
        tree1.merge_from_branch(tree2.branch)
        rev3 = tree1.commit('')
        tree3, = self._get_revtrees(tree1, [rev2])
        self.assertEqual(rev2, tree3.inventory[name + 'id'].revision)
        self.assertFileAncestry([rev1, rev2], tree1, name)

    def test_last_modified_revision_after_converged_merge_dir_changes(self):
        # merge a dir changes the last modified.
        tree1 = self.make_branch_and_tree('t1')
        self.build_tree(['t1/dir/'])
        self._commit_sprout_rename_merge_converged(tree1, 'dir')

    def test_last_modified_revision_after_converged_merge_file_changes(self):
        # merge a file changes the last modified.
        tree1 = self.make_branch_and_tree('t1')
        self.build_tree(['t1/file'])
        self._commit_sprout_rename_merge_converged(tree1, 'file')

    def test_last_modified_revision_after_converged_merge_link_changes(self):
        # merge a link changes the last modified.
        self.requireFeature(tests.SymlinkFeature)
        tree1 = self.make_branch_and_tree('t1')
        os.symlink('target', 't1/link')
        self._commit_sprout_rename_merge_converged(tree1, 'link')

    def make_dir(self, name):
        self.build_tree([name + '/'])

    def make_file(self, name):
        self.build_tree([name])

    def make_link(self, name):
        self.requireFeature(tests.SymlinkFeature)
        os.symlink('target', name)

    def _check_kind_change(self, make_before, make_after):
        tree = self.make_branch_and_tree('.')
        path = 'name'
        make_before(path)
        def change_kind():
            # Look Before You Leap (LBYL) is appropriate here because unlink
            # will raise different exceptions on different OSes (linux: EISDIR,
            # win32: EACCES, OSX: EPERM) when invoked on a directory.
            if osutils.isdir(path): # Takes care of symlinks
                os.rmdir(path)
            else:
                os.unlink(path)
            make_after(path)
        self._add_commit_change_check_changed(tree, path, change_kind)

    def test_last_modified_dir_file(self):
        self._check_kind_change(self.make_dir, self.make_file)

    def test_last_modified_dir_link(self):
        self._check_kind_change(self.make_dir, self.make_link)

    def test_last_modified_link_file(self):
        self._check_kind_change(self.make_link, self.make_file)

    def test_last_modified_link_dir(self):
        self._check_kind_change(self.make_link, self.make_dir)

    def test_last_modified_file_dir(self):
        self._check_kind_change(self.make_file, self.make_dir)

    def test_last_modified_file_link(self):
        self._check_kind_change(self.make_file, self.make_link)
