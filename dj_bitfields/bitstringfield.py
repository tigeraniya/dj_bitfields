from contextlib import closing

from bitstring import Bits
from django.db import models
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper as PGDatabaseWrapper
from django.db.backends.signals import connection_created
from psycopg2 import extensions as ext

try:
    from rest_framework import serializers,exceptions
    rfw = True
except ImportError:
    rfw = False

__all__ = ['Bits', 'BitStringField', 'BitStringExpression']


def adapt_bits(bits):
    """psycopg2 adapter function for ``bitstring.Bits``.
    Encode SQL parameters from ``bitstring.Bits`` instances to SQL strings.
    """
    if bits.length % 4 == 0:
        return ext.AsIs("X'%s'" % (bits.hex,))
    return ext.AsIs("B'%s'" % (bits.bin,))
ext.register_adapter(Bits, adapt_bits)


def cast_bits(value, cur):
    """psycopg2 caster for bit strings.
    Turns query results from the database into ``bitstring.Bits`` instances.
    """
    if value is None:
        return None
    return Bits(bin=value)


def register_bitstring_types(connection):
    """Register the BIT and VARBIT casters on the provided connection.
    This ensures that BIT and VARBIT instances returned from the database will
    be represented in Python as ``bitstring.Bits`` instances.
    """
    with closing(connection.cursor()) as cur:
        cur.execute("SELECT NULL::BIT")
        bit_oid = cur.description[0].type_code
        cur.execute("SELECT NULL::VARBIT")
        varbit_oid = cur.description[0].type_code
    bit_caster = ext.new_type((bit_oid, varbit_oid), 'BIT', cast_bits)
    ext.register_type(bit_caster, connection)


def register_types_on_connection_creation(connection, sender, *args, **kwargs):
    if not issubclass(sender, PGDatabaseWrapper):
        return
    register_bitstring_types(connection.connection)
connection_created.connect(register_types_on_connection_creation)

if rfw:
    class SerializerBitStringField(serializers.Field):
        def __init__(self,*arg,fix_length=None,**kw):
            self.fix_length = fix_length
            super().__init__(*arg,**kw)

        def to_representation(self, value):
            return value.hex

        def to_internal_value(self, data):
            print(len(data)*4,self.fix_length)
            if self.fix_length and len(data)*4 != self.fix_length:
                raise exceptions.ValidationError("invalid size for bitstring")
            return Bits(hex=data)


class BitStringField(models.Field):

    """A Postgres bit string."""

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.setdefault('max_length', 1)
        self.varying = kwargs.pop('varying', False)

        if 'default' in kwargs:
            default = kwargs.pop('default')
        elif kwargs.get('null', False):
            default = None
        elif self.max_length is not None and not self.varying:
            default = '0' * self.max_length
        else:
            default = '0'
        kwargs['default'] = self.to_python(default)

        super(BitStringField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        if self.varying:
            if self.max_length is not None:
                return 'VARBIT(%d)' % (self.max_length,)
            return 'VARBIT'
        elif self.max_length is not None:
            return 'BIT(%d)' % (self.max_length,)
        return 'BIT'

    def to_python(self, value):
        if value is None or isinstance(value, Bits):
            return value
        elif isinstance(value, str):
            if value.startswith('0x'):
                return Bits(hex=value)
            return Bits(bin=value)
        raise TypeError("Cannot coerce into bit string: %r" % (value,))

    def get_prep_value(self, value):
        return self.to_python(value)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return map(self.get_prep_value, value)
        raise TypeError("Lookup type %r not supported on bit strings" % lookup_type)

    def get_default(self):
        default = super(BitStringField, self).get_default()
        return self.to_python(default)

from django.db.models import Lookup

@BitStringField.register_lookup
class BitstringAND(Lookup):
    lookup_name = 'and'

    def process_lhs(self, compiler, connection, lhs=None):
        ret = super().process_lhs(compiler,connection,lhs=lhs)
        print("process_lhs",ret)
        return ret

    def process_rhs(self, compiler, connection):
        ret = super().process_rhs(compiler, connection)
        print("process_rhs", ret)
        return ret

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return " position(B'1' IN {0} & '{1}' ) > 0".format(lhs, self.rhs.bin),[]


@BitStringField.register_lookup
class BitstringOR(Lookup):
    lookup_name = 'or'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return " position(B'1' IN %s | '%s') > 0"%(self.lhs.alias + '.' + self.lhs.field.name, self.rhs.bin),params



@BitStringField.register_lookup
class BitstringXOR(Lookup):
    lookup_name = 'xor'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return " position(B'1' IN %s # '%s') > 0"%(self.lhs.alias + '.' + self.lhs.field.name, self.rhs.bin),params


@BitStringField.register_lookup
class BitstringContains(Lookup):
    lookup_name = 'superset'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        print("params",params," position(B'1' IN ~{0} & '{1}') <= 0 and position(B'1' IN '{1}') >= 0".format(lhs, self.rhs.bin))
        return " position(B'1' IN ~{0} & '{1}') <= 0 and position(B'1' IN '{1}') >= 0".format(lhs, self.rhs.bin), []

@BitStringField.register_lookup
class BitstringContains(Lookup):
    lookup_name = 'subset'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        print(" position(B'1' IN ~B'{1}' & B'{0}') <= 0 and position(B'1' IN B'{0}') >= 0".format(lhs, self.rhs.bin))
        return " position(B'1' IN ~B'{1}' & {0}) <= 0 and position(B'1' IN {0}) >= 0".format(lhs, self.rhs.bin), []

@BitStringField.register_lookup
class BitstringContains(Lookup):
    lookup_name = 'intersects'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return " position(B'1' IN  {0} & '{1}') > 0".format(lhs, self.rhs.bin), []

@BitStringField.register_lookup
class BitstringContains(Lookup):
    lookup_name = 'disjoint'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return " position(B'1' IN  {0} & '{1}') <= 0".format(lhs, self.rhs.bin), []

