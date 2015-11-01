"""
Tests for L{pyflakes.checker}.
"""

from pyflakes.checker import Checker
from pyflakes.test.harness import TestCase


class FakeNode(object):

    """Mock an AST node."""

    def __init__(self, lineno=1, col_offset=0):
        self.lineno = lineno
        self.col_offset = col_offset


class StoredKwargsChecker(Checker):

    """Store keyword arguments for use in tests."""

    def __init__(self, tree, withDoctest, **kwargs):
        if 'test_result' in kwargs:
            self._test_result = kwargs['test_result']
            del kwargs['test_result']
        self._test_kwargs = kwargs
        super(StoredKwargsChecker, self).__init__(
            tree, withDoctest=withDoctest)


class DeferredFunctionChecker(StoredKwargsChecker):

    """
    Checker that ignores tree and injects a deferred function.

    Args:
        injected_function: function to inject
        node: node to pass to injected function
        assignment: use deferAssignment instead of deferFunction
    """

    def NAME(self, node):
        f = self._test_kwargs['injected_function']
        node = self._test_kwargs.get('node')
        if self._test_kwargs.get('assignment'):
            self.deferAssignment(lambda: f(self))
        elif node:
            self.deferFunction(
                lambda *args, **kwargs: f(self, *args, **kwargs),
                self._test_kwargs.get('node'))
        else:
            self.deferFunction(lambda: f(self))


class TestDeferFunction(TestCase):
    """Tests for L{Checker} deferred checks."""

    checker_cls = DeferredFunctionChecker

    def test_deferred_assignment(self):
        """The deferred assignment invokes function."""
        node = FakeNode(10, 2)

        def do(self):
            assert self._deferredAssignments
            assert not self._deferredFunctions
            self._test_result = node

        checker = self.flakes('foo = 1', injected_function=do, assignment=True)

        assert hasattr(checker, '_test_result')
        assert checker._test_result == node
        assert checker._test_result.lineno == 10

    def test_deferred_function_with_node(self):
        """The deferred function invokes function with node."""
        def do(self, node):
            assert not self._deferredAssignments
            assert self._deferredFunctions
            self._test_result = node

        node = FakeNode(10, 2)

        checker = self.flakes('foo = 1', injected_function=do, node=node)

        assert hasattr(checker, '_test_result')
        assert checker._test_result == node
        assert checker._test_result.lineno == 10

    def test_deferred_function_without_node(self):
        """The deferred function invokes function with node."""
        def do(self):
            assert not self._deferredAssignments
            assert self._deferredFunctions
            self._test_result = True

        checker = self.flakes('foo = 1', injected_function=do)

        assert hasattr(checker, '_test_result')
        assert checker._test_result is True


class ImmediateDeferredFunctionChecker(StoredKwargsChecker):

    """
    Checker that ignores tree and injects a deferred function.

    Args:
        injected_function: function to inject
        immediate_name: name to process immediately
    """

    def NAME(self, node):
        f = self._test_kwargs['injected_function']
        self.deferFunction(lambda node: f(self, node), node)

        assert self._deferredFunctions
        name = self._test_kwargs.get('immediate_name')
        if node.id == name:
            print('running immediate', name)
            self.runDeferredFunctionImmediate(name)


class TestUnDeferFunction(TestCase):
    """Tests for L{Checker} deferred checks."""

    checker_cls = ImmediateDeferredFunctionChecker

    def test_deferred_function_immediate(self):
        """The deferred function is invoked immediately."""
        def do(self, node):
            # do('b') should be run first, then be removed when 'a' and 'c' run
            assert self._deferredFunctions[0][0] == self.handleFunction
            assert self._deferredFunctions[1][3].id == 'a'

            if node.id == 'b':
                assert len(self._deferredFunctions) == 3
                assert self._deferredFunctions[2][3].id == 'b'
            elif node.id in ['a', 'c']:
                assert len(self._deferredFunctions) == 3
                assert self._deferredFunctions[2][3].id == 'c'

        self.flakes('''
            def foo():
                a = 1
                b = 1
                c = 1
                return
        ''', injected_function=do, immediate_name='b')

    def test_deferred_function_immediate_scope(self):
        """The deferred function is invoked immediately."""
        def do(self, node):
            # do('b') in foo() should be run first,
            # then be removed when 'a', 'c', and 'b' in bar() are run

            assert self._deferredFunctions[0][0] == self.handleFunction
            assert self._deferredFunctions[1][0] == self.handleFunction
            assert self._deferredFunctions[2][3].id == 'a'

            if node.id == 'b':
                if node.parent.parent.name == 'foo':
                    # b in foo() should be processed first
                    assert not self._test_result
                    assert len(self._deferredFunctions) == 4
                    assert self._deferredFunctions[3][3].id == 'b'
                elif node.parent.parent.name == 'bar':
                    # b in foo() should have already be processed
                    assert self._test_result
                    assert len(self._deferredFunctions) == 5
                    assert self._deferredFunctions[3][3].id == 'c'
                    assert self._deferredFunctions[4][3].id == 'b'

                self._test_result.append(node)

            elif node.id in ['a', 'c']:
                # 'a' and 'c' are processed after 'b' in foo() has been removed
                assert len(self._deferredFunctions) == 4
                assert self._deferredFunctions[3][3].id == 'c'

        checker = self.flakes('''
            def foo():
                def bar():
                    b = 1

                a = 1
                b = 1
                c = 1
                return
        ''', injected_function=do, immediate_name='b', test_result=[])

        assert len(checker._test_result) == 2
