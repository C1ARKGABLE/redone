#!/usr/bin/env python3
# redone: A correct regex implementation in Python
# Copyright (C) 2014 Cyphar

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# 1. The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from . import conv
from . import parser
from . import regex

__all__ = ["compile", "match"]

def _compile(pattern):
	# XXX: The current conversion operation isn't properly optimised, so it isn't
	#      run by default.

	graph = parser._parse(pattern)
	#graph = conv.nfa2dfa(graph)

	return regex.RegexMatcher(graph)

def compile(pattern):
	"""
	Compile the given regular expression into a RegexMatcher which can be used to
	run regex operations on any given string without needing to recompile the
	expression.
	"""

	return _compile(pattern)

def match(pattern, string):
	"""
	Partial matches the given string against the given regex pattern. It returns
	either the slice of the partial match or None if not matched.
	"""

	if isinstance(pattern, regex.RegexMatcher):
		return pattern.match(string)

	return _compile(pattern).match(string)

def fullmatch(pattern, string):
	"""
	Fully matches a given string against a given regex pattern. It returns either
	the slice of the match (the given string) or None if not matched.
	"""

	if isinstance(pattern, regex.RegexMatcher):
		return pattern.fullmatch(string)

	return _compile(pattern).fullmatch(string)

def search(pattern, string):
	"""
	Searches the given string for a match against the given regex pattern. It
	returns either the slice of the left-most match or None if there was no match.
	"""

	if isinstance(pattern, regex.RegexMatcher):
		return pattern.search(string)

	return _compile(pattern).search(string)
