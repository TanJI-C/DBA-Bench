"""Database identities shared by benchmark targets and infrastructure."""

from enum import Enum


class DatabaseSystem(str, Enum):
    POSTGRESQL = "postgresql"
    TIDB = "tidb"
