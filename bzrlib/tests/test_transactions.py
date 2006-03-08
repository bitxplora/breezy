# Copyright (C) 2005 by Canonical Ltd
#   Authors: Robert Collins <robert.collins@canonical.com>
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

"""Tests for the behaviour of the Transaction concept in bzr."""

# import system imports here
import os
import sys

#import bzrlib specific imports here
import bzrlib.errors as errors
from bzrlib.tests import TestCase, TestCaseInTempDir
import bzrlib.transactions as transactions


class DummyWeave(object):
    """A class that can be instantiated and compared."""

    def __init__(self, message):
        self._message = message

    def __eq__(self, other):
        if other is None:
            return False
        return self._message == other._message


class TestSymbols(TestCase):

    def test_public_symbols(self):
        from bzrlib.transactions import ReadOnlyTransaction
        from bzrlib.transactions import PassThroughTransaction


class TestReadOnlyTransaction(TestCase):

    def setUp(self):
        self.transaction = transactions.ReadOnlyTransaction()
        super(TestReadOnlyTransaction, self).setUp()

    def test_register_clean(self):
        self.transaction.register_clean("anobject")

    def test_register_dirty_raises(self):
        self.assertRaises(errors.ReadOnlyError, 
                          self.transaction.register_dirty,"anobject")
    
    def test_map(self):
        self.assertNotEqual(None, getattr(self.transaction, "map", None))
    
    def test_add_and_get(self):
        weave = "a weave"
        self.transaction.map.add_weave("id", weave)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))

    def test_finish_returns(self):
        self.transaction.finish()

    def test_zero_size_cache(self):
        self.transaction.set_cache_size(0)
        weave = DummyWeave('a weave')
        self.transaction.map.add_weave("id", weave)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        weave = None
        # add an object, should fall right out if there are no references
        self.transaction.register_clean(self.transaction.map.find_weave("id"))
        self.assertEqual(None, self.transaction.map.find_weave("id"))
        # but if we have a reference it should stick around
        weave = DummyWeave("another weave")
        self.transaction.map.add_weave("id", weave)
        self.transaction.register_clean(self.transaction.map.find_weave("id"))
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        del weave
        # its not a weakref system
        self.assertEqual(DummyWeave("another weave"),
                         self.transaction.map.find_weave("id"))
        
    def test_small_cache(self):
        self.transaction.set_cache_size(1)
        # add an object, should not fall right out if there are no references
        #sys.getrefcounts(foo)
        self.transaction.map.add_weave("id", DummyWeave("a weave"))
        self.transaction.register_clean(self.transaction.map.find_weave("id"))
        self.assertEqual(DummyWeave("a weave"),
                         self.transaction.map.find_weave("id"))
        self.transaction.map.add_weave("id2", DummyWeave("a weave also"))
        self.transaction.register_clean(self.transaction.map.find_weave("id2"))
        # currently a fifo
        self.assertEqual(None, self.transaction.map.find_weave("id"))
        self.assertEqual(DummyWeave("a weave also"),
                         self.transaction.map.find_weave("id2"))

    def test_small_cache_with_references(self):
        # if we have a reference it should stick around
        weave = "a weave"
        weave2 = "another weave"
        self.transaction.map.add_weave("id", weave)
        self.transaction.map.add_weave("id2", weave2)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        self.assertEqual(weave2, self.transaction.map.find_weave("id2"))
        weave = None
        # its not a weakref system
        self.assertEqual("a weave", self.transaction.map.find_weave("id"))

    def test_precious_with_zero_size_cache(self):
        self.transaction.set_cache_size(0)
        weave = DummyWeave('a weave')
        self.transaction.map.add_weave("id", weave)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        weave = None
        # add an object, should not fall out even with no references.
        self.transaction.register_clean(self.transaction.map.find_weave("id"),
                                        precious=True)
        self.assertEqual(DummyWeave('a weave'),
                         self.transaction.map.find_weave("id"))

    def test_precious_revision_history(self):
        """Disabled test until revision-history is a real object."""
        print "Disabled: test_precious_revision_history"
        return
        self.transaction.set_cache_size(0)
        history = []
        self.transaction.map.add_revision_history(history)
        self.assertEqual(history, self.transaction.map.find_revision_history())
        history = None
        # add an object, should not fall out even with no references.
        self.transaction.register_clean(
            self.transaction.map.find_revision_history(), precious=True)
        self.assertEqual([], self.transaction.map.find_revision_history())


class TestPassThroughTransaction(TestCase):

    def test_construct(self):
        transactions.PassThroughTransaction()

    def test_register_clean(self):
        transaction = transactions.PassThroughTransaction()
        transaction.register_clean("anobject")
    
    def test_register_dirty(self):
        transaction = transactions.PassThroughTransaction()
        transaction.register_dirty("anobject")
    
    def test_map(self):
        transaction = transactions.PassThroughTransaction()
        self.assertNotEqual(None, getattr(transaction, "map", None))
    
    def test_add_and_get(self):
        transaction = transactions.PassThroughTransaction()
        weave = "a weave"
        transaction.map.add_weave("id", weave)
        self.assertEqual(None, transaction.map.find_weave("id"))
        
    def test_finish_returns(self):
        transaction = transactions.PassThroughTransaction()
        transaction.finish()

    def test_cache_is_ignored(self):
        transaction = transactions.PassThroughTransaction()
        transaction.set_cache_size(100)
        weave = "a weave"
        transaction.map.add_weave("id", weave)
        self.assertEqual(None, transaction.map.find_weave("id"))

        
class TestWriteTransaction(TestCase):

    def setUp(self):
        self.transaction = transactions.WriteTransaction()
        super(TestWriteTransaction, self).setUp()

    def test_register_clean(self):
        self.transaction.register_clean("anobject")
    
    def test_register_dirty(self):
        self.transaction.register_dirty("anobject")
    
    def test_map(self):
        self.assertNotEqual(None, getattr(self.transaction, "map", None))
    
    def test_add_and_get(self):
        weave = "a weave"
        self.transaction.map.add_weave("id", weave)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        
    def test_finish_returns(self):
        self.transaction.finish()

    def test_zero_size_cache(self):
        self.transaction.set_cache_size(0)
        # add an object, should fall right out if there are no references
        weave = DummyWeave('a weave')
        self.transaction.map.add_weave("id", weave)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        weave = None
        self.transaction.register_clean(self.transaction.map.find_weave("id"))
        self.assertEqual(None, self.transaction.map.find_weave("id"))
        # but if we have a reference to a clean object it should stick around
        weave = DummyWeave("another weave")
        self.transaction.map.add_weave("id", weave)
        self.transaction.register_clean(self.transaction.map.find_weave("id"))
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        del weave
        # its not a weakref system
        self.assertEqual(DummyWeave("another weave"),
                         self.transaction.map.find_weave("id"))

    def test_zero_size_cache_dirty_objects(self):
        self.transaction.set_cache_size(0)
        # add a dirty object, which should not fall right out.
        weave = DummyWeave('a weave')
        self.transaction.map.add_weave("id", weave)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        weave = None
        self.transaction.register_dirty(self.transaction.map.find_weave("id"))
        self.assertNotEqual(None, self.transaction.map.find_weave("id"))
    
    def test_clean_to_dirty(self):
        # a clean object may become dirty.
        weave = DummyWeave('A weave')
        self.transaction.map.add_weave("id", weave)
        self.transaction.register_clean(weave)
        self.transaction.register_dirty(weave)
        self.assertTrue(self.transaction.is_dirty(weave))
        self.assertFalse(self.transaction.is_clean(weave))

    def test_small_cache(self):
        self.transaction.set_cache_size(1)
        # add an object, should not fall right out if there are no references
        #sys.getrefcounts(foo)
        self.transaction.map.add_weave("id", DummyWeave("a weave"))
        self.transaction.register_clean(self.transaction.map.find_weave("id"))
        self.assertEqual(DummyWeave("a weave"),
                         self.transaction.map.find_weave("id"))
        self.transaction.map.add_weave("id2", DummyWeave("a weave also"))
        self.transaction.register_clean(self.transaction.map.find_weave("id2"))
        # currently a fifo
        self.assertEqual(None, self.transaction.map.find_weave("id"))
        self.assertEqual(DummyWeave("a weave also"),
                         self.transaction.map.find_weave("id2"))

    def test_small_cache_with_references(self):
        # if we have a reference it should stick around
        weave = "a weave"
        weave2 = "another weave"
        self.transaction.map.add_weave("id", weave)
        self.transaction.map.add_weave("id2", weave2)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        self.assertEqual(weave2, self.transaction.map.find_weave("id2"))
        weave = None
        # its not a weakref system
        self.assertEqual("a weave", self.transaction.map.find_weave("id"))

    def test_precious_with_zero_size_cache(self):
        self.transaction.set_cache_size(0)
        weave = DummyWeave('a weave')
        self.transaction.map.add_weave("id", weave)
        self.assertEqual(weave, self.transaction.map.find_weave("id"))
        weave = None
        # add an object, should not fall out even with no references.
        self.transaction.register_clean(self.transaction.map.find_weave("id"),
                                        precious=True)
        self.assertEqual(DummyWeave('a weave'),
                         self.transaction.map.find_weave("id"))
