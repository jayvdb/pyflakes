"""Tests for L{pyflakes.checker}."""

from pyflakes.checker import Checker, getNodeName
from pyflakes.test.harness import TestCase


class StoredKwargsChecker(Checker):

    """Checker that stores keyword arguments for use in tests."""

    def __init__(self, tree, withDoctest, **kwargs):
        self._test_result = None
        if 'test_result' in kwargs:
            self._test_result = kwargs['test_result']
            del kwargs['test_result']
        self._test_kwargs = kwargs
        super(StoredKwargsChecker, self).__init__(
            tree, withDoctest=withDoctest)


class DeprecatedFuturesAllowedChecker(StoredKwargsChecker):

    """
    Checker that ignores tree and injects a deferred function.

    Args:
        capture_at: node to activate state capture
        enable_at: node to force enabling of futures
    """

    def NAME(self, node):
        name = getNodeName(node)
        if self._test_result is None:
            if name == self._test_kwargs['capture_at']:
                self._test_result = self.futuresAllowed
        super(DeprecatedFuturesAllowedChecker, self).NAME(node)

    def IMPORTFROM(self, node):
        name = node.module
        if name == self._test_kwargs.get('enable_at'):
            self.futuresAllowed = True

        if self._test_result is None:
            if name == self._test_kwargs['capture_at']:
                self._test_result = self.futuresAllowed
        super(DeprecatedFuturesAllowedChecker, self).IMPORTFROM(node)

    def STR(self, node):
        name = node.s
        if self._test_result is None:
            if name == self._test_kwargs['capture_at']:
                self._test_result = self.futuresAllowed


class TestFuturesAllowed(TestCase):
    """Tests for L{Checker} futuresAllowed flag."""

    checker_cls = DeprecatedFuturesAllowedChecker

    def test_future_at_beginning(self):
        """The futuresAllowed enabled initially."""
        checker = self.flakes('''
        """docstring allowed."""
        from __future__ import print_function
        ''', capture_at='__future__')

        assert checker._test_result is True

    def test_future_disabled_after_node(self):
        """The futuresAllowed disabled after node."""
        checker = self.flakes('1\nf = 1', capture_at='f')

        assert hasattr(checker, '_test_result')
        assert checker._test_result is False

        checker = self.flakes('def f(): a = 1; return a', capture_at='a')

        assert checker._test_result is False

    def test_future_set_allowed(self):
        """Set futuresAllowed permitted."""
        checker = self.flakes('''
        1
        from __future__ import print_function
        a = 1
        ''', enable_at='__future__', capture_at='a')

        assert checker._test_result is False
