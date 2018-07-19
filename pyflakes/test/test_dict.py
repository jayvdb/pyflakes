"""
Tests for dict duplicate keys Pyflakes behavior.
"""
from sys import version_info

from pyflakes import messages as m
from pyflakes.checker import PYPY
from pyflakes.test.harness import TestCase, skipIf


class Test(TestCase):

    def test_duplicate_keys(self):
        self.flakes(
            "{'yes': 1, 'yes': 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    @skipIf(version_info < (3,),
            "bytes and strings with same 'value' are not equal in python3")
    def test_duplicate_keys_bytes_vs_unicode_py3(self):
        self.flakes("{b'a': 1, u'a': 2}")

    @skipIf(version_info < (3,),
            "bytes and strings with same 'value' are not equal in python3")
    def test_duplicate_values_bytes_vs_unicode_py3(self):
        self.flakes(
            "{1: b'a', 1: u'a'}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    @skipIf(version_info >= (3,),
            "bytes and strings with same 'value' are equal in python2")
    def test_duplicate_keys_bytes_vs_unicode_py2(self):
        self.flakes(
            "{b'a': 1, u'a': 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    @skipIf(version_info >= (3,),
            "bytes and strings with same 'value' are equal in python2")
    def test_duplicate_values_bytes_vs_unicode_py2(self):
        self.flakes("{1: b'a', 1: u'a'}")

    def test_multiple_duplicate_keys(self):
        self.flakes(
            "{'yes': 1, 'yes': 2, 'no': 2, 'no': 3}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_in_function(self):
        self.flakes(
            '''
            def f(thing):
                pass
            f({'yes': 1, 'yes': 2})
            ''',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_in_lambda(self):
        self.flakes(
            "lambda x: {(0,1): 1, (0,1): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_bytearray(self):
        self.flakes(
            '{bytearray(0): 1, bytearray(0): 2}',
            m.UnhashableTypeError,
            m.UnhashableTypeError,
        )

    def test_duplicate_keys_bytes(self):
        self.flakes(
            '{bytes(0): 1, bytes(0): 2}',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_tuples(self):
        self.flakes(
            "{(0,1): 1, (0,1): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

        self.flakes(
            '{tuple(0, 1): 1, tuple(0, 1): 2}',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_frozenset(self):
        self.flakes(
            '{frozenset([0, 1]): 1, frozenset([0, 1]): 2}',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_set(self):
        self.flakes(
            '{set([0, 1]): 1, set([0, 1]): 2}',
            m.UnhashableTypeError,
            m.UnhashableTypeError,
        )

    def test_duplicate_keys_list(self):
        self.flakes(
            '{[0, 1]: 1, [0, 1]: 2}',
            m.UnhashableTypeError,
            m.UnhashableTypeError,
        )
        self.flakes(
            '{list(): 1, list(): 2}',
            m.UnhashableTypeError,
            m.UnhashableTypeError,
        )

    def test_duplicate_keys_dict(self):
        self.flakes(
            "{{0: 1}: 1, {0: 1}: 2}",
            m.UnhashableTypeError,
            m.UnhashableTypeError,
        )
        self.flakes(
            "{dict(): 1, dict(): 2}",
            m.UnhashableTypeError,
            m.UnhashableTypeError,
        )

    def test_duplicate_keys_tuples_int_and_float(self):
        self.flakes(
            "{(0,1): 1, (0,1.0): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_ints(self):
        self.flakes(
            "{1: 1, 1: 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )
        self.flakes(
            "{int(1): 1, int(1): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    @skipIf(version_info >= (3,),
            "long is Python 2 only")
    def test_duplicate_keys_long_literal(self):
        self.flakes(
            "{long(1): 1, long(1): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )
        self.flakes(
            "{1L: 1, long(1): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_float(self):
        self.flakes(
            "{float(1): 1, float(1): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_complex(self):
        self.flakes(
            "{complex(1): 1, complex(1): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_bools(self):
        self.flakes(
            "{True: 1, True: 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )
        self.flakes(
            "{bool(1): 1, bool(1): 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_Ellipsis(self):
        self.flakes(
            "{Ellipsis: 1, Ellipsis: 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    @skipIf(version_info < (3,),
            "ast.Ellipsis is Python 3 only")
    def test_duplicate_keys_ast_Ellipsis(self):
        self.flakes(
            "{...: 1, ...: 2}",
        )

    def test_duplicate_keys_underscore(self):
        self.flakes(
            "{_: 1, _: 2}",
            m.MultiValueRepeatedKeyVariable,
            m.MultiValueRepeatedKeyVariable,
            # These are bogus
            m.UndefinedName,
            m.UndefinedName,
        )

    def test_duplicate_keys_bools_false(self):
        # Needed to ensure 2.x correctly coerces these from variables
        self.flakes(
            "{False: 1, False: 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_none(self):
        self.flakes(
            "{None: 1, None: 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_safe_callable(self):
        safe_callables = [
            'abs', 'bin', 'callable', 'chr', 'hash', 'hex', 'id',
            'oct', 'repr', 'round', 'type',
        ]
        if version_info >= (3,) and not PYPY:
            safe_callables += ['ascii', 'range']

        for func in safe_callables:
            self.flakes(
                '{%s(1): 1, %s(1): 2}' % (func, func),
                m.MultiValueRepeatedKeyLiteral,
                m.MultiValueRepeatedKeyLiteral,
            )

    def test_duplicate_keys_safe_callable_list(self):
        safe_callables = [
            'all', 'any', 'len', 'sum', 'min', 'max',
        ]
        for func in safe_callables:
            self.flakes(
                '{%s([1]): 1, %s([1]): 2}' % (func, func),
                m.MultiValueRepeatedKeyLiteral,
                m.MultiValueRepeatedKeyLiteral,
            )

    @skipIf(version_info >= (3,),
            "coerce is Python 2 only")
    def test_duplicate_keys_coerce(self):
        self.flakes(
            '{coerce(10, 10.001010): 1, coerce(10, 10.001010): 2}',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_divmod(self):
        self.flakes(
            '{divmod(1, 2): 1, divmod(1, 2): 2}',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_pow(self):
        self.flakes(
            '{pow(1, 2): 1, pow(1, 2): 2}',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_ord(self):
        self.flakes(
            '{ord("a"): 1, ord("a"): 2}',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_keys_format(self):
        self.flakes(
            '{format(10, "b"): 1, format(10, "b"): 2}',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_unhashable_callable(self):
        unhashable_callables = [
            'slice',
        ]
        if version_info < (3,):
            unhashable_callables.append('range')
        for func in unhashable_callables:
            self.flakes(
                '{%s(1): 1, %s(1): 2}' % (func, func),
                m.UnhashableTypeError,
                m.UnhashableTypeError,
            )

    def test_unequal_callable(self):
        unequal_callables = [
            'enumerate', 'AssertionError', 'globals', 'locals', 'dir',
            'object', 'filter', 'iter', 'map', 'object', 'reversed', 'sorted',
            'vars', 'zip',
        ]
        if version_info < (3,):
            # note 'round' is unequal under future
            unequal_callables += ('xrange', )
        for func in unequal_callables:
            self.flakes(
                '{%s(1): 1, %s(1): 2}' % (func, func),
            )

    def test_unsafe_callable(self):
        unsafe_callables = [
            'compile', 'delattr', 'eval', 'exit', 'help', 'input', 'open',
            'quit', 'getattr', 'hasattr', 'isinstance', 'issubclass', 'setattr'
        ]
        if version_info < (3,):
            unsafe_callables.append('raw_input')
        if version_info >= (3,):
            # {print(): 1} is a SyntaxError on Python 2 as the test harness
            # does not import __future__.print_function
            unsafe_callables += ('exec', 'print', '__loader__', '__import__')

        for func in unsafe_callables:
            self.flakes(
                '{%s(1): 1, %s(1): 2}' % (func, func),
            )

    def test_duplicate_keys_exception_class(self):
        self.flakes(
            "{AssertionError: 1, AssertionError: 2}",
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_variable_keys(self):
        self.flakes(
            '''
            a = 1
            {a: 1, a: 2}
            ''',
            m.MultiValueRepeatedKeyVariable,
            m.MultiValueRepeatedKeyVariable,
        )

    def test_duplicate_variable_values(self):
        self.flakes(
            '''
            a = 1
            b = 2
            {1: a, 1: b}
            ''',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_variable_values_same_value(self):
        # Current behaviour is not to look up variable values. This is to
        # confirm that.
        self.flakes(
            '''
            a = 1
            b = 1
            {1: a, 1: b}
            ''',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_duplicate_key_float_and_int(self):
        """
        These do look like different values, but when it comes to their use as
        keys, they compare as equal and so are actually duplicates.
        The literal dict {1: 1, 1.0: 1} actually becomes {1.0: 1}.
        """
        self.flakes(
            '''
            {1: 1, 1.0: 2}
            ''',
            m.MultiValueRepeatedKeyLiteral,
            m.MultiValueRepeatedKeyLiteral,
        )

    def test_no_duplicate_key_error_same_value(self):
        self.flakes('''
        {'yes': 1, 'yes': 1}
        ''')

    def test_no_duplicate_key_errors(self):
        self.flakes('''
        {'yes': 1, 'no': 2}
        ''')

    def test_no_duplicate_keys_tuples_same_first_element(self):
        self.flakes("{(0,1): 1, (0,2): 1}")

    def test_no_duplicate_key_errors_func_call(self):
        self.flakes('''
        def test(thing):
            pass
        test({True: 1, None: 2, False: 1})
        ''')

    def test_no_duplicate_key_errors_bool_or_none(self):
        self.flakes("{True: 1, None: 2, False: 1}")

    def test_no_duplicate_key_errors_ints(self):
        self.flakes('''
        {1: 1, 2: 1}
        ''')

    def test_no_duplicate_key_errors_vars(self):
        self.flakes('''
        test = 'yes'
        rest = 'yes'
        {test: 1, rest: 2}
        ''')

    def test_no_duplicate_key_errors_tuples(self):
        self.flakes('''
        {(0,1): 1, (0,2): 1}
        ''')

    def test_no_duplicate_key_errors_instance_attributes(self):
        self.flakes('''
        class Test():
            pass
        f = Test()
        f.a = 1
        {f.a: 1, f.a: 1}
        ''')
