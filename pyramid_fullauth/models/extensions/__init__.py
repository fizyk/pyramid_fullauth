# Copyright (c) by SQLAlchemy authors and contributors.
#
# This module's code is part of SQLAlchemy's documentation
# http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/hybrid.html#hybrid-value-objects
# and released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""CaseInsensitive comparator for sqlalchemy models."""

from sqlalchemy import func
from sqlalchemy.ext.hybrid import Comparator


class CaseInsensitive(Comparator):  # pylint:disable=abstract-method
    """Hybrid value representing a lower case representation."""

    def __init__(self, word):  # pylint:disable=super-init-not-called
        """Initialise comparator object."""
        if isinstance(word, str):
            self.word = word.lower()
        elif isinstance(word, CaseInsensitive):
            self.word = word.word
        else:
            self.word = func.lower(word)

    def operate(self, op, other):  # pylint:disable=arguments-differ
        """Operate."""
        if not isinstance(other, CaseInsensitive):
            other = CaseInsensitive(other)
        return op(self.word, other.word)

    def __clause_element__(self):
        """Get clause element for comparator.."""
        return self.word

    def __str__(self):
        """Cast element to."""
        return self.word
