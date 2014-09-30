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

from . import nfa

class RegexParseException(Exception):
	pass


class RegexParser(object):
	"""
	An object used internally within redone in order to parse regular expressions
	and convert them into the equivalent NFANode graph.
	"""

	# BNF for extended regex:
	# <re>     ::= <simple> ( "|" <re> )?
	# <simple> ::= <basic>+
	# <basic>  ::= <elem> ("*" | "+" | "?")?
	# <elem>   ::= "(" <re> ")"
	# <elem>   ::= "\" ("*" | "+" | "?" | "(" | ")" | "|" | "\")
	# <elem>   ::= ¬("*" | "+" | "?" | "(" | ")" | "|" | "\")

	def __init__(self, tokens):
		self._tokens = tokens
		self._pos = 0
		self._length = len(tokens)

	def end(self):
		"""
		Returns whether or not the parser state is at the end of the tokens.
		"""

		return self._pos == self._length

	def peek(self):
		"""
		Returns the current token in the parser state.
		"""

		if not self.end():
			return self._tokens[self._pos]

	def next(self, num=1):
		"""
		Advances the parser state forward by num tokens. Raises an error if the
		new parser state is out-of-bounds in the token list.
		"""

		if not self.end():
			self._pos += num

		#if self._pos > self._length:
		#	raise RegexParseException("Parser state is out-of-bounds on token list.")

	def _parse_elem(self):
		metachars = {"*", "+", "?", "(", ")", "|", "\\"}

		start = nfa.NFANode(tag="elem_start", accept=False)
		end = nfa.NFANode(tag="elem_end", accept=True)

		# Groups
		if self.peek() == "(":
			self.next()

			graph = self._parse_re()

			if self.peek() != ")":
				raise RegexParseException("Missing closing ')' in regex group.")

			self.next()

			# Make graph link with the start and end.
			start.add_edge(nfa.EPSILON_EDGE, graph)
			graph.patch(end, label=nfa.EPSILON_EDGE)

		# Metacharacter Escapes
		elif self.peek() == "\\":
			self.next()

			char = self.peek()
			self.next()

			if char not in metachars:
				raise RegexParseException("Invalid escape sequence: %s." % ('\\' + char))

			start.add_edge(char, end)

		# All other characters.
		elif self.peek() not in metachars:
			char = self.peek()
			self.next()

			start.add_edge(char, end)

		# Invalid characters.
		else:
			return None

		return start

	def _parse_basic(self):
		node = self._parse_elem()

		if self.peek() in ["*", "+", "?"]:
			if node is None:
				raise RegexParseException("Modifier applied to an non-element.")

			modifier = self.peek()
			self.next()

			start = nfa.NFANode(tag="modifier_start", accept=False)
			end = nfa.NFANode(tag="modifier_end", accept=True)

			# Attach element to start and end.
			start.add_edge(nfa.EPSILON_EDGE, node)
			node.patch(end, label=nfa.EPSILON_EDGE)

			# Kleene Star
			if modifier == "*":
				start.add_edge(nfa.EPSILON_EDGE, end)
				end.add_edge(nfa.EPSILON_EDGE, start)

			# Kleene Plus
			elif modifier == "+":
				end.add_edge(nfa.EPSILON_EDGE, start)

			# Optional
			elif modifier == "?":
				start.add_edge(nfa.EPSILON_EDGE, end)

			node = start

		if node is None:
			return None

		return node


	def _parse_simple(self):
		node = self._parse_basic()

		if node is None:
			return None

		while not self.end():
			right = self._parse_basic()

			if right is None:
				break

			# Concatinate nodes.
			node.patch(right, label=nfa.EPSILON_EDGE)

		return node

	def _parse_re(self):
		node = self._parse_simple()

		if node is None:
			return None

		if self.peek() == "|":
			self.next()

			left = node
			right = self._parse_re()

			if right is None:
				raise RegexParseException("Union without right side in expression.")

			# Create new starting and accepting nodes.
			start = nfa.NFANode(tag="union_start", accept=False)
			end = nfa.NFANode(tag="union_end", accept=True)

			# Add links to left and right.
			start.add_edge(nfa.EPSILON_EDGE, left)
			start.add_edge(nfa.EPSILON_EDGE, right)

			# Update left and right to point to the new end.
			left.patch(end, label=nfa.EPSILON_EDGE)
			right.patch(end, label=nfa.EPSILON_EDGE)

			# Update node to point to the new start node.
			node = start

		return node

	def parse(self):
		"""
		Parses a regular expression and produces an NFANode graph that represents that
		will match text according to the given regex rules.
		"""
		return self._parse_re()


def compile_regex(pattern):
	"""
	Compile a given pattern into an NFA which represents the pattern's state
	machine. The return statement is an NFANode graph which will match according
	to the pattern's rules.
	"""

	tokens = list(pattern)
	parser = RegexParser(tokens)

	return parser.parse()
