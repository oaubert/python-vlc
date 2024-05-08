#! /usr/bin/env python
# This Python file uses the following encoding: utf-8

#
# Code generator for python ctypes bindings for VLC
# Copyright (C) 2009 the VideoLAN team
# $Id: $
#
# Authors: Olivier Aubert <contact at olivieraubert.net>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#

"""Unittest module for testing the generator."""

import logging
import unittest
from pathlib import Path

from generator.generate import (
    Enum,
    Func,
    Par,
    Parser,
    Struct,
    Union,
    Val,
    class_re,
    clean_doxygen_comment,
    def_re,
    snake_to_camel_case,
    strip_whitespaces,
)

logger = logging.getLogger(__name__)


# Test internal generator only in python3
class TestREs(unittest.TestCase):
    def test_class_re_method(self):
        self.assertIsNone(class_re.match("    def __new__(cls, arg=None):\n"))

    def test_class_re(self):
        match = class_re.match("class Instance:\n")
        self.assertEqual(match.group(1), "Instance")

    def test_def_re(self):
        self.assertEqual(
            def_re.findall(
                "\n    def __new__(cls, *args):\n\n   def get_instance(self):\n\n    def add_media(self, mrl):\n\n"
            ),
            ["__new__", "get_instance", "add_media"],
        )


class TestUtils(unittest.TestCase):
    """Test utility functions"""

    def test_strip_whitespaces(self):
        test_cases = [
            ([], []),
            (["a", "b"], ["a", "b"]),
            (["", "a", "b", ""], ["a", "b"]),
            (["\n", "\t", "a", "b", "\n", " "], ["a", "b"]),
            ([" ", "a", "b", "\n", "\r", "\f"], ["a", "b"]),
            (["\n", "a", "\n", "b", "\n"], ["a", "\n", "b"]),
            ((), ()),
            (("", "a", "b", ""), ("a", "b")),
            (("\n", "\t", "a", "b", "\n", " "), ("a", "b")),
            ((" ", "a", "b", "\n", "\r", "\f"), ("a", "b")),
            (("\n", "a", " ", "b", "\n"), ("a", " ", "b")),
            ("", ""),
            ("ab", "ab"),
            ("\n\tab\n ", "ab"),
            (" ab\n\r\f", "ab"),
            ("\na b\n", "a b"),
        ]

        for input, expected_result in test_cases:
            self.assertEqual(strip_whitespaces(input), expected_result)


class TestParser(unittest.TestCase):
    def get_parser(self, code_file: Path | str) -> Parser:
        return Parser(
            code_file,
            "./tests/test_parser_inputs/libvlc_version_without_extra.h",
        )

    def test_parse_enums(self):
        expected_enums = [
            Enum(
                "libvlc_enum_no_values_specified",
                "enum",
                [
                    Val("G", "0"),
                    Val("H", "1"),
                    Val("I", "2"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_all_values_specified",
                "enum",
                [
                    Val("J", "2"),
                    Val("K", "4"),
                    Val("L", "6"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_values_specified_or_not",
                "enum",
                [
                    Val("M", "5"),
                    Val("N", "6"),
                    Val("O", "8"),
                    Val("P", "9"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_with_docs",
                "enum",
                [
                    Val("Q", "5"),
                    Val("R", "6"),
                    Val("S", "8"),
                    Val("T", "9"),
                ],
                """Some Doxygen
documentation
that spans
multiple lines""",
            ),
            Enum(
                "libvlc_enum_with_hex_values",
                "enum",
                [
                    Val("U", "0x1"),
                    Val("V", "0xf"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_with_bit_shifted_values",
                "enum",
                [
                    Val("W", "7471104"),
                    Val("X", "6750208"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_with_deprecated_values",
                "enum",
                [],
                "",
            ),
            Enum(
                "libvlc_enum_with_documented_values",
                "enum",
                [
                    Val("B1", "0", "This is a single line comment for B1."),
                    Val(
                        "B2",
                        "1",
                        """This is a multi line
comment for B2.""",
                    ),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_no_values_specified_t",
                "enum",
                [
                    Val("GG", "0"),
                    Val("HH", "1"),
                    Val("II", "2"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_all_values_specified_t",
                "enum",
                [
                    Val("JJ", "2"),
                    Val("KK", "4"),
                    Val("LL", "6"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_values_specified_or_not_t",
                "enum",
                [
                    Val("MM", "5"),
                    Val("NN", "6"),
                    Val("OO", "8"),
                    Val("PP", "9"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_with_docs_t",
                "enum",
                [
                    Val("QQ", "5"),
                    Val("RR", "6"),
                    Val("SS", "8"),
                    Val("TT", "9"),
                ],
                """Some Doxygen
documentation
that spans
multiple lines""",
            ),
            Enum(
                "libvlc_enum_with_hex_values_t",
                "enum",
                [
                    Val("UU", "0x1"),
                    Val("VV", "0xf"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_with_bit_shifted_values_t",
                "enum",
                [
                    Val("WW", "7471104"),
                    Val("XX", "6750208"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_t",
                "enum",
                [
                    Val("ZZ", "0"),
                ],
                "",
            ),
            Enum(
                "libvlc_enum_with_deprecated_values_t",
                "enum",
                [],
                "",
            ),
            Enum(
                "libvlc_enum_with_documented_values_t",
                "enum",
                [
                    Val("BB1", "0", "This is a single line comment for BB1."),
                    Val(
                        "BB2",
                        "1",
                        """This is a multi line
comment for BB2.""",
                    ),
                ],
                "",
            ),
        ]

        p = self.get_parser("./tests/test_parser_inputs/enums.h")
        self.assertCountEqual(p.enums, expected_enums)

    def test_parse_structs(self):
        expected_structs = [
            Struct(
                "libvlc_struct_no_values_specified",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_all_values_specified",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_docs",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "double", [False]),
                ],
                """Some Doxygen
documentation
that spans
multiple lines""",
            ),
            Struct(
                "libvlc_struct_with_const",
                "struct",
                [
                    Par("x", "char", [True]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_pointers",
                "struct",
                [
                    Par("x", "int*", [True, False]),
                    Par("y", "double*", [False, True]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_anonymous_nested_union",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "char", [False]),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_named_nested_union",
                "struct",
                [
                    Par("a", "int", [False]),
                    Union(
                        "u",
                        "union",
                        [
                            Par("b", "char", [False]),
                            Par("c", "char", [False]),
                        ],
                        "",
                    ),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_anonymous_nested_struct",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "char", [False]),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_named_nested_struct",
                "struct",
                [
                    Par("a", "int", [False]),
                    Struct(
                        "s",
                        "struct",
                        [
                            Par("b", "char", [False]),
                            Par("c", "char", [False]),
                        ],
                        "",
                    ),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_nested_anonymous_union_and_struct",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "char", [False]),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_nested_named_union_and_struct",
                "struct",
                [
                    Par("a", "int", [False]),
                    Union(
                        "u",
                        "union",
                        [
                            Par("b", "char", [False]),
                        ],
                        "",
                    ),
                    Struct(
                        "s",
                        "struct",
                        [
                            Par("c", "char", [False]),
                        ],
                        "",
                    ),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_nested_anonymous_union_and_nested_struct_inside",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "char", [False]),
                    Par("d", "char", [False]),
                    Par("e", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_nested_named_union_and_nested_struct_inside",
                "struct",
                [
                    Par("a", "int", [False]),
                    Union(
                        "u",
                        "union",
                        [
                            Par("b", "char", [False]),
                            Struct(
                                "s1",
                                "struct",
                                [
                                    Par("c", "char", [False]),
                                ],
                            ),
                            Struct(
                                "s2",
                                "struct",
                                [
                                    Par("d", "char", [False]),
                                ],
                            ),
                        ],
                        "",
                    ),
                    Par("e", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_callbacks",
                "struct",
                [
                    Func("cb1", "void", [], "Some docs for cb1."),
                    Func("cb2", "void", [], "Some docs for cb2."),
                    Func("cb3", "void", [], "Some docs for cb3."),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_complex_callbacks",
                "struct",
                [
                    Func(
                        "cb1",
                        "char*",
                        [
                            Par("a", "int", [False]),
                            Par("b", "double", [False]),
                        ],
                        "",
                    ),
                    Func(
                        "cb2",
                        "char**",
                        [
                            Par("a", "int", [False]),
                            Par("b", "double", [False]),
                        ],
                        "",
                    ),
                    Func(
                        "cb3",
                        "char***",
                        [
                            Par("a", "int", [False]),
                            Par("b", "double", [False]),
                        ],
                        "",
                    ),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_cb_taking_cb_as_argument",
                "struct",
                [
                    Func(
                        "cb",
                        "char*",
                        [
                            Func(
                                "cb_param",
                                "int",
                                [
                                    Par("a", "int", [False]),
                                    Par("b", "double", [False]),
                                    Par("c", "char", [False]),
                                ],
                                "",
                            )
                        ],
                        "",
                    )
                ],
                "",
            ),
            Struct(
                "libvlc_struct_no_values_specified_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_all_values_specified_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_docs_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "double", [False]),
                ],
                """Some Doxygen
documentation
that spans
multiple lines""",
            ),
            Struct(
                "libvlc_struct_t",
                "struct",
                [
                    Par("x", "char", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_const_t",
                "struct",
                [
                    Par("x", "char", [True]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_pointers_t",
                "struct",
                [
                    Par("x", "int*", [True, False]),
                    Par("y", "double*", [False, True]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_anonymous_nested_union_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "char", [False]),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_named_nested_union_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Union(
                        "u",
                        "union",
                        [
                            Par("b", "char", [False]),
                            Par("c", "char", [False]),
                        ],
                        "",
                    ),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_anonymous_nested_struct_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "char", [False]),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_named_nested_struct_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Struct(
                        "s",
                        "struct",
                        [
                            Par("b", "char", [False]),
                            Par("c", "char", [False]),
                        ],
                        "",
                    ),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_nested_anonymous_union_and_struct_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "char", [False]),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_nested_named_union_and_struct_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Union(
                        "u",
                        "union",
                        [
                            Par("b", "char", [False]),
                        ],
                        "",
                    ),
                    Struct(
                        "s",
                        "struct",
                        [
                            Par("c", "char", [False]),
                        ],
                        "",
                    ),
                    Par("d", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_nested_anonymous_union_and_nested_struct_inside_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Par("b", "char", [False]),
                    Par("c", "char", [False]),
                    Par("d", "char", [False]),
                    Par("e", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_nested_named_union_and_nested_struct_inside_t",
                "struct",
                [
                    Par("a", "int", [False]),
                    Union(
                        "u",
                        "union",
                        [
                            Par("b", "char", [False]),
                            Struct(
                                "s1",
                                "struct",
                                [
                                    Par("c", "char", [False]),
                                ],
                            ),
                            Struct(
                                "s2",
                                "struct",
                                [
                                    Par("d", "char", [False]),
                                ],
                            ),
                        ],
                        "",
                    ),
                    Par("e", "double", [False]),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_callbacks_t",
                "struct",
                [
                    Func("cb1", "void", [], "Some docs for cb1."),
                    Func("cb2", "void", [], "Some docs for cb2."),
                    Func("cb3", "void", [], "Some docs for cb3."),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_complex_callbacks_t",
                "struct",
                [
                    Func(
                        "cb1",
                        "char*",
                        [
                            Par("a", "int", [False]),
                            Par("b", "double", [False]),
                        ],
                        "",
                    ),
                    Func(
                        "cb2",
                        "char**",
                        [
                            Par("a", "int", [False]),
                            Par("b", "double", [False]),
                        ],
                        "",
                    ),
                    Func(
                        "cb3",
                        "char***",
                        [
                            Par("a", "int", [False]),
                            Par("b", "double", [False]),
                        ],
                        "",
                    ),
                ],
                "",
            ),
            Struct(
                "libvlc_struct_with_cb_taking_cb_as_argument_t",
                "struct",
                [
                    Func(
                        "cb",
                        "char*",
                        [
                            Func(
                                "cb_param",
                                "int",
                                [
                                    Par("a", "int", [False]),
                                    Par("b", "double", [False]),
                                    Par("c", "char", [False]),
                                ],
                                "",
                            )
                        ],
                        "",
                    )
                ],
                "",
            ),
        ]

        p = self.get_parser("./tests/test_parser_inputs/structs.h")
        self.assertCountEqual(p.structs, expected_structs)

    def test_parse_funcs(self):
        expected_funcs = [
            Func("libvlc_simple", "void", [], ""),
            Func("libvlc_simple_with_void", "void", [], ""),
            Func("libvlc_attribute_on_the_previous_line", "void", [], ""),
            Func(
                "libvlc_with_docs",
                "void",
                [],
                """Some Doxygen
documentation
that spans
multiple lines""",
            ),
            Func(
                "libvlc_simple_types",
                "char",
                [
                    Par("a", "int", [False]),
                    Par("b", "float", [False]),
                ],
                "",
            ),
            Func(
                "libvlc_pointer_as_return_type",
                "char*",
                [
                    Par("a", "int", [False]),
                    Par("b", "float", [False]),
                ],
                "",
            ),
            Func(
                "libvlc_pointer_as_return_type_with_qualifier",
                "char*",
                [
                    Par("a", "int", [False]),
                    Par("b", "float", [False]),
                ],
                "",
            ),
            Func(
                "libvlc_pointers_and_qualifiers_everywhere",
                "char*",
                [
                    Par("c1", "char*", [True, False]),
                    Par("c2", "char*", [True, False]),
                ],
                "",
            ),
            Func(
                "libvlc_multiple_pointers",
                "char**",
                [
                    Par("c1", "char**", [False, False, False]),
                    Par("c2", "char***", [False, False, False, False]),
                ],
                "",
            ),
            Func(
                "libvlc_multiple_pointers_and_qualifiers",
                "char**",
                [
                    Par("c1", "char**", [True, False, True]),
                    Par(
                        "c2",
                        "char***",
                        [False, True, True, True],
                    ),
                ],
                "",
            ),
            Func(
                "libvlc_function_pointer_as_param",
                "void",
                [Func("cb", "void", [], "")],
                "",
            ),
            Func(
                "libvlc_complex_function_pointer_as_param",
                "void",
                [
                    Func(
                        "cb",
                        "char*",
                        [Par("", "char***", [False, True, True, False])],
                        "",
                    )
                ],
                "",
            ),
            Func(
                "libvlc_complex_function_pointer_as_param_with_named_params",
                "void",
                [
                    Func(
                        "cb",
                        "char**",
                        [
                            Par("c1", "char***", [False, True, True, False]),
                            Par("c2", "char***", [False, True, False, False]),
                        ],
                        "",
                    ),
                    Par("i", "int", [False]),
                    Par("d", "double", [False]),
                ],
                "",
            ),
        ]

        p = self.get_parser("./tests/test_parser_inputs/funcs.h")
        self.assertCountEqual(p.funcs, expected_funcs)

    def test_parse_callbacks(self):
        expected_callbacks = [
            Func("libvlc_simple_cb", "void", [], ""),
            Func("libvlc_simple_with_void_cb", "void", [], ""),
            Func(
                "libvlc_simple_with_void_pointers_cb",
                "void*",
                [
                    Par("p", "void*", [False, False]),
                ],
                "",
            ),
            Func(
                "libvlc_simple_types_cb",
                "char",
                [
                    Par("a", "int", [False]),
                    Par("b", "float", [False]),
                ],
                "",
            ),
            Func(
                "libvlc_with_docs_cb",
                "char",
                [
                    Par("a", "int", [False]),
                    Par("b", "float", [False]),
                ],
                """Some Doxygen
documentation
that spans
multiple lines""",
            ),
            Func(
                "libvlc_one_pointer_cb",
                "char*",
                [
                    Par("c1", "char*", [False, False]),
                    Par("c2", "char*", [False, False]),
                    Par("c3", "char*", [False, False]),
                ],
                "",
            ),
            Func(
                "libvlc_one_pointer_and_const_cb",
                "char*",
                [
                    Par("c1", "char*", [True, False]),
                    Par("c2", "char*", [False, False]),
                    Par("c3", "char*", [False, False]),
                ],
                "",
            ),
            Func(
                "libvlc_multiple_pointers_cb",
                "char**",
                [
                    Par("c1", "char**", [False, False, False]),
                    Par("c2", "char***", [False, False, False, False]),
                    Par("c3", "char****", [False, False, False, False, False]),
                ],
                "",
            ),
            Func(
                "libvlc_multiple_pointers_with_const_cb",
                "char**",
                [
                    Par("c1", "char**", [True, True, False]),
                    Par("c2", "char***", [False, True, True, True]),
                    Par("c3", "char****", [False, True, False, True, False]),
                ],
                "",
            ),
            Func(
                "libvlc_function_pointer_as_param_cb",
                "void",
                [
                    Func("cb", "void", [], ""),
                ],
                "",
            ),
            Func(
                "libvlc_complex_function_pointer_as_param_cb",
                "void",
                [
                    Func(
                        "cb",
                        "char*",
                        [
                            Par("", "char***", [False, True, True, False]),
                            Par("", "int", [False]),
                            Par("", "double", [False]),
                        ],
                        "",
                    ),
                ],
                "",
            ),
        ]

        p = self.get_parser("./tests/test_parser_inputs/callbacks.h")
        self.assertCountEqual(p.callbacks, expected_callbacks)

    def test_parse_version(self):
        p = Parser(
            # Can use any valid path, it doesn't matter
            "./tests/test_parser_inputs/libvlc_version_without_extra.h",
            # There it matters
            "./tests/test_parser_inputs/libvlc_version_without_extra.h",
        )
        self.assertEqual(p.version, "3.0.16")

        p = Parser(
            # Can use any valid path, it doesn't matter
            "./tests/test_parser_inputs/libvlc_version_with_extra.h",
            # There it matters
            "./tests/test_parser_inputs/libvlc_version_with_extra.h",
        )
        self.assertEqual(p.version, "4.2.14.3")


class TestUtilities(unittest.TestCase):
    def test_clean_doxygen_comment(self):
        test_cases = [
            # non javadoc style comments should be ignored
            ("// regular comment", ""),
            (
                """/* multiline
comment
 */""",
                "",
            ),
            # Then valid javadoc style comments...
            (
                "/** single line doxygen comment */",
                "single line doxygen comment",
            ),
            (
                "/**single line comment with trailing spaces           */",
                "single line comment with trailing spaces",
            ),
            (
                """/**
 * extra spaces everywhere           
 *
         */""",
                "extra spaces everywhere",
            ),
            (
                """/** multiline
 * doxygen
 * comment
 */""",
                """multiline
doxygen
comment""",
            ),
            (
                """/** preserve
 *
 * blank lines
 *
 * in between
 */""",
                """preserve

blank lines

in between""",
            ),
            # real world comments (coming from liblvc)
            (
                r"""/**
 * Start playing (if there is any item in the playlist).
 *
 * Additionnal playlist item options can be specified for addition to the
 * item before it is played.
 *
 * \param p_instance the playlist instance
 * \param i_id the item to play. If this is a negative number, the next
 *        item will be selected. Otherwise, the item with the given ID will be
 *        played
 * \param i_options the number of options to add to the item
 * \param ppsz_options the options to add to the item
 */""",
                r"""Start playing (if there is any item in the playlist).

Additionnal playlist item options can be specified for addition to the
item before it is played.

\param p_instance the playlist instance
\param i_id the item to play. If this is a negative number, the next
item will be selected. Otherwise, the item with the given ID will be
played
\param i_options the number of options to add to the item
\param ppsz_options the options to add to the item""",
            ),
        ]

        for input, expected_output in test_cases:
            self.assertEqual(clean_doxygen_comment(input), expected_output)

    def test_snake_to_camel_case(self):
        test_cases = [
            ("", ""),
            ("one", "one"),
            ("one234", "one234"),
            ("_one", "_one"),
            ("__one", "__one"),
            ("one_", "one_"),
            ("one__", "one__"),
            ("one_two_three_four", "oneTwoThreeFour"),
            ("One_Two_Three_Four", "oneTwoThreeFour"),
        ]

        for input, expected_output in test_cases:
            self.assertEqual(snake_to_camel_case(input), expected_output)


if __name__ == "__main__":
    logging.basicConfig()
    unittest.main()
