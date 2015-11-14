import sys
import textwrap

from pyflakes import messages as m
from pyflakes.checker import (
    DoctestScope,
    FunctionScope,
    ModuleScope,
)
from pyflakes.test.test_other import Test as TestOther
from pyflakes.test.test_imports import Test as TestImports
from pyflakes.test.test_undefined_names import Test as TestUndefinedNames
from pyflakes.test.harness import TestCase, skip, erroneous_result

try:
    sys.pypy_version_info
    PYPY = True
except AttributeError:
    PYPY = False


class _DoctestMixin(object):

    withDoctest = True

    def doctestify(self, input):
        lines = []
        for line in textwrap.dedent(input).splitlines():
            if line.strip() == '':
                pass
            elif line.startswith('# doctest output: '):
                line = line[18:]
            elif (line.startswith(' ') or
                  line.startswith('except:') or
                  line.startswith('except ') or
                  line.startswith('finally:') or
                  line.startswith('else:') or
                  line.startswith('elif ')):
                line = "... %s" % line
            else:
                line = ">>> %s" % line
            lines.append(line)
        doctestificator = textwrap.dedent('''\
            def doctest_something():
                """
                   %s
                """
            ''')
        return doctestificator % "\n       ".join(lines)

    def flakes(self, input, *args, **kw):
        return super(_DoctestMixin, self).flakes(self.doctestify(input), *args, **kw)


class Test(TestCase):

    withDoctest = True

    def test_scope_class(self):
        """Check that a doctest is given a DoctestScope."""
        checker = self.flakes("""
        m = None

        def doctest_stuff():
            '''
                >>> d = doctest_stuff()
            '''
            f = m
            return f
        """)

        scopes = checker.deadScopes
        module_scopes = [
            scope for scope in scopes if scope.__class__ is ModuleScope]
        doctest_scopes = [
            scope for scope in scopes if scope.__class__ is DoctestScope]
        function_scopes = [
            scope for scope in scopes if scope.__class__ is FunctionScope]

        self.assertEqual(len(module_scopes), 1)
        self.assertEqual(len(doctest_scopes), 1)

        module_scope = module_scopes[0]
        doctest_scope = doctest_scopes[0]

        self.assertIsInstance(doctest_scope, DoctestScope)
        self.assertIsInstance(doctest_scope, ModuleScope)
        self.assertNotIsInstance(doctest_scope, FunctionScope)
        self.assertNotIsInstance(module_scope, DoctestScope)

        self.assertIn('m', module_scope)
        self.assertIn('doctest_stuff', module_scope)

        self.assertIn('d', doctest_scope)

        self.assertEqual(len(function_scopes), 1)
        self.assertIn('f', function_scopes[0])

    def test_nested_doctest_ignored(self):
        """Check that nested doctests are ignored."""
        checker = self.flakes("""
        m = None

        def doctest_stuff():
            '''
                >>> def function_in_doctest():
                ...     \"\"\"
                ...     >>> ignored_undefined_name
                ...     \"\"\"
                ...     df = m
                ...     return df
                ...
                >>> function_in_doctest()
            '''
            f = m
            return f
        """)

        scopes = checker.deadScopes
        module_scopes = [
            scope for scope in scopes if scope.__class__ is ModuleScope]
        doctest_scopes = [
            scope for scope in scopes if scope.__class__ is DoctestScope]
        function_scopes = [
            scope for scope in scopes if scope.__class__ is FunctionScope]

        self.assertEqual(len(module_scopes), 1)
        self.assertEqual(len(doctest_scopes), 1)

        module_scope = module_scopes[0]
        doctest_scope = doctest_scopes[0]

        self.assertIn('m', module_scope)
        self.assertIn('doctest_stuff', module_scope)
        self.assertIn('function_in_doctest', doctest_scope)

        self.assertEqual(len(function_scopes), 2)

        self.assertIn('f', function_scopes[0])
        self.assertIn('df', function_scopes[1])

    def test_global_module_scope_pollution(self):
        """Check that global in doctest does not pollute module scope."""
        checker = self.flakes("""
        def doctest_stuff():
            '''
                >>> def function_in_doctest():
                ...     global m
                ...     m = 50
                ...     df = 10
                ...     m = df
                ...
                >>> function_in_doctest()
            '''
            f = 10
            return f

        """)

        scopes = checker.deadScopes
        module_scopes = [
            scope for scope in scopes if scope.__class__ is ModuleScope]
        doctest_scopes = [
            scope for scope in scopes if scope.__class__ is DoctestScope]
        function_scopes = [
            scope for scope in scopes if scope.__class__ is FunctionScope]

        self.assertEqual(len(module_scopes), 1)
        self.assertEqual(len(doctest_scopes), 1)

        module_scope = module_scopes[0]
        doctest_scope = doctest_scopes[0]

        self.assertIn('doctest_stuff', module_scope)
        self.assertIn('function_in_doctest', doctest_scope)

        self.assertEqual(len(function_scopes), 2)

        self.assertIn('f', function_scopes[0])
        self.assertIn('df', function_scopes[1])
        self.assertIn('m', function_scopes[1])

        self.assertNotIn('m', module_scope)

    @erroneous_result
    def test_doctest_empty_source_with_want(self):
        """Empty doctest example source with a want is an error."""
        # TODO: doctest skips an empty source line, and its wanted result.
        # Detecting this requires loosely parsing docstrings for empty '>>>'.
        self.flakes("""
        def doctest_stuff():
            '''
                >>> 1
                1
                >>>
                >>>
                1
                >>> 1
                1
            '''
        """, m.Message)

    def test_global_undefined(self):
        self.flakes("""
        global m

        def doctest_stuff():
            '''
                >>> m
            '''
        """, m.UndefinedName)

    def test_importBeforeDoctest(self):
        self.flakes("""
        import foo

        def doctest_stuff():
            '''
                >>> foo
            '''
        """)

    @skip("todo")
    def test_importBeforeAndInDoctest(self):
        self.flakes('''
        import foo

        def doctest_stuff():
            """
                >>> import foo
                >>> foo
            """

        foo
        ''', m.RedefinedWhileUnused)

    def test_importInDoctestAndAfter(self):
        self.flakes('''
        def doctest_stuff():
            """
                >>> import foo
                >>> foo
            """

        import foo
        foo()
        ''')

    def test_offsetInDoctests(self):
        exc = self.flakes('''

        def doctest_stuff():
            """
                >>> x # line 5
            """

        ''', m.UndefinedName).messages[0]
        self.assertEqual(exc.lineno, 5)
        self.assertEqual(exc.col, 12)

    def test_offsetInLambdasInDoctests(self):
        exc = self.flakes('''

        def doctest_stuff():
            """
                >>> lambda: x # line 5
            """

        ''', m.UndefinedName).messages[0]
        self.assertEqual(exc.lineno, 5)
        self.assertEqual(exc.col, 20)

    def test_offsetAfterDoctests(self):
        exc = self.flakes('''

        def doctest_stuff():
            """
                >>> x = 5
            """

        x

        ''', m.UndefinedName).messages[0]
        self.assertEqual(exc.lineno, 8)
        self.assertEqual(exc.col, 0)

    def test_syntaxErrorInDoctest(self):
        exceptions = self.flakes(
            '''
            def doctest_stuff():
                """
                    >>> from # line 4
                    >>>     fortytwo = 42
                    >>> except Exception:
                """
            ''',
            m.DoctestSyntaxError,
            m.DoctestSyntaxError,
            m.DoctestSyntaxError).messages
        exc = exceptions[0]
        self.assertEqual(exc.lineno, 4)
        self.assertEqual(exc.col, 26)

        # PyPy error column offset is 0,
        # for the second and third line of the doctest
        # i.e. at the beginning of the line
        exc = exceptions[1]
        self.assertEqual(exc.lineno, 5)
        if PYPY:
            self.assertEqual(exc.col, 13)
        else:
            self.assertEqual(exc.col, 16)
        exc = exceptions[2]
        self.assertEqual(exc.lineno, 6)
        if PYPY:
            self.assertEqual(exc.col, 13)
        else:
            self.assertEqual(exc.col, 18)

    def test_indentationErrorInDoctest(self):
        exc = self.flakes('''
        def doctest_stuff():
            """
                >>> if True:
                ... pass
            """
        ''', m.DoctestSyntaxError).messages[0]
        self.assertEqual(exc.lineno, 5)
        if PYPY:
            self.assertEqual(exc.col, 13)
        else:
            self.assertEqual(exc.col, 16)

    def test_offsetWithMultiLineArgs(self):
        (exc1, exc2) = self.flakes(
            '''
            def doctest_stuff(arg1,
                              arg2,
                              arg3):
                """
                    >>> assert
                    >>> this
                """
            ''',
            m.DoctestSyntaxError,
            m.UndefinedName).messages
        self.assertEqual(exc1.lineno, 6)
        self.assertEqual(exc1.col, 19)
        self.assertEqual(exc2.lineno, 7)
        self.assertEqual(exc2.col, 12)

    def test_doctestCanReferToFunction(self):
        self.flakes("""
        def foo():
            '''
                >>> foo
            '''
        """)

    def test_doctestCanReferToClass(self):
        self.flakes("""
        class Foo():
            '''
                >>> Foo
            '''
            def bar(self):
                '''
                    >>> Foo
                '''
        """)

    def test_noOffsetSyntaxErrorInDoctest(self):
        exceptions = self.flakes(
            '''
            def buildurl(base, *args, **kwargs):
                """
                >>> buildurl('/blah.php', ('a', '&'), ('b', '=')
                '/blah.php?a=%26&b=%3D'
                >>> buildurl('/blah.php', a='&', 'b'='=')
                '/blah.php?b=%3D&a=%26'
                """
                pass
            ''',
            m.DoctestSyntaxError,
            m.DoctestSyntaxError).messages
        exc = exceptions[0]
        self.assertEqual(exc.lineno, 4)
        exc = exceptions[1]
        self.assertEqual(exc.lineno, 6)


class TestUnderscore(_DoctestMixin, TestCase):

    withDoctest = True

    def test_underscore_undefined(self):
        """Underscore does not exist at beginning of scope."""
        self.flakes('_', m.UndefinedName)

    def test_underscore_after_assignment(self):
        """Underscore does not exist after assignment."""
        self.flakes('a = 1\n_', m.UndefinedName)

    def test_underscore_after_definition(self):
        """Underscore does not exist after a function definition."""
        self.flakes('''
        def foo(): pass

        _
        ''', m.UndefinedName)

    def test_underscore_after_import(self):
        """Underscore does not exist after an import."""
        self.flakes('''
        import foo
        foo.x

        _
        ''', m.UndefinedName)

    def test_underscore_after_unbound_value(self):
        self.flakes('''
        1
        # doctest output: 1
        _
        ''')

    @erroneous_result
    def test_underscore_after_print_undefined(self):
        """Underscore does not exist after a print output."""
        self.flakes('''
        print(1)
        # doctest output: 1
        _
        ''', m.UndefinedName)

    def test_underscore_nested_inherited(self):
        """Underscore does inherit outer scope."""
        self.flakes('''
        def foo():
            print(_)

        1
        # doctest output: 1
        _
        # doctest output: 1
        foo()
        # doctest output: 1
        ''')

    @erroneous_result
    def test_underscore_nested_definition(self):
        """Underscore used in nested scope before it exists."""
        self.flakes('''
        def foo():
            1
            print(_)

        foo()
        # doctest output: 1
        ''', m.UndefinedName)


class TestOther(_DoctestMixin, TestOther):
    pass


class TestImports(_DoctestMixin, TestImports):

    def test_futureImport(self):
        """XXX This test can't work in a doctest"""

    def test_futureImportUsed(self):
        """XXX This test can't work in a doctest"""


class TestUndefinedNames(_DoctestMixin, TestUndefinedNames):
    """Run TestUndefinedNames with each test wrapped in a doctest."""
    pass
