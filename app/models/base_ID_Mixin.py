from sqlalchemy import Column, BigInteger
from sqlalchemy.ext.declarative import declared_attr

class BigIntPKMixin:
    @declared_attr
    def id(cls):
        return Column(
            BigInteger,          # Use BigInteger normally
            primary_key=True,
            index=True,
            autoincrement=True,
            mysql_unsigned=True  # <-- ONLY for MySQL
        )
