"""Regex class -- Interpret and apply a regular expression."""

import re


class Regex():
    """Interpret and apply a regular expression."""

    def __init__(self, expression=''):
        self.pattern = None
        self.replacement = None
        self.count = 1
        self.flags = 0
        self.set_expression(expression)

    @property
    def is_valid(self) -> bool:
        """Returns True if the object contains a valid regular expression."""
        return self.pattern is not None

    def apply(self, text) -> str:
        """Convert the text using the regular expression."""
        if not self.is_valid:
            return text
        if self.replacement is None:
            return self._apply_search(text)
        return self._apply_substitution(text)

    def _apply_search(self, text) -> str:
        if self.count:
            if found := re.search(self.pattern, text, self.flags):
                if found.groups():
                    return '\t'.join(found.groups())
                return found[0]
            return ''
        lines = re.findall(self.pattern, text, self.flags)
        if lines:
            if isinstance(lines[0], tuple):
                lines = ['\t'.join(line) for line in lines]
            return '\n'.join(lines)
        return ''

    def _apply_substitution(self, text) -> str:
        return re.sub(self.pattern, self.replacement, text, self.count, self.flags)

    def set_expression(self, expression) -> bool:
        """Set the object's regular expression.

        Return True if the expression is a valid expression.
        """
        if self.set_substitution_expression(expression):
            return True
        return self.set_search_expression(expression)

    def set_search_expression(self, expression):
        """Set the object's regular expression to the specified search expression.

        Return True if the expression is a valid search expression.
        """
        # Groups:                   1-12-                -2  3-      -3
        if found := re.fullmatch(r's(.)(.*?(?<!\\)(?:\\\\))\1([agims]*)', expression):
            self.pattern = found[2]
            self.replacement = None
            self._set_regex_flags(found[3])
            return True
        return False

    def set_substitution_expression(self, expression):
        """Set the object's regular expression to the specified substitution expression.

        Return True if the expression is a valid substitution expression.
        """
        # Groups:                   1-12-                 -2  3-                 -3  4-      -4
        if found := re.fullmatch(r's(.)(.*?(?<!\\)(?:\\\\)*)\1(.*?(?<!\\)(?:\\\\)*)\1([agims]*)',
                                 expression):
            self.pattern = found[2]
            self.replacement = found[3]
            self._set_regex_flags(found[4])
            return True
        return False

    def _set_regex_flags(self, flags_text):
        self.count = 1
        self.flags = 0
        if 'a' in flags_text:
            self.flags |= re.ASCII
        if 'g' in flags_text:
            self.count = 0
        if 'i' in flags_text:
            self.flags |= re.IGNORECASE
        if 'm' in flags_text:
            self.flags |= re.MULTILINE
        if 's' in flags_text:
            self.flags |= re.DOTALL
