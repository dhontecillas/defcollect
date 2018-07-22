"""Data types for Data Definition."""

import abc

from datetime import date, datetime

class DataType(object):
    """Base class for data types.

    Each subclass must define a `DATA_TYPE` property, that
    defines the name for the type.

    When creating a new data type, some constraints can be given at
    initialization. Those are a dictionary with properties that
    are interpretable by each subtype. So, in order to customize
    the internal vars to set, each subtype can override
    `_set_constraints` function.

    See example implementations: TextType, NumberType, DateType or EnumType.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, constraints=None, uid=None):
        """
        :param name: The name for this data field.
        :param constraints: a dictionary with a field type dependant format
            that sets constraints for the input valued for this field.
        :param uid: Unique ID for this data field.
        """
        self.name = name
        self.uid = uid
        self.nullable = False
        self._set_constraints(constraints)

    @abc.abstractmethod
    def _set_constraints(self, constraints):
        """Checks that constraints given for this field type are correct."""
        if constraints is None:
            constraints = {}
        self.constraints = constraints
        self.nullable = constraints.get('nullable', False)

    @abc.abstractmethod
    def validate(self, value):
        """Validate that a value conforms to type and constraints.

        raises ValueError if value can not be interpreted as the correct
            type.
        """
        if value is None and not self.nullable:
            raise ValueError('Non nullable')
        return value

    @staticmethod
    def list_types():
        """Returns a list of available type classes."""
        data_types = []
        for dpt in DataType.__subclasses__():
            if hasattr(dpt, 'DATA_TYPE'):
                data_types.append(dpt)
        return data_types

    @staticmethod
    def type_class(datatype_name):
        """Returns the DataType class for a given data type."""
        type_classes = DataType.list_types()
        for tclass in type_classes:
            if tclass.DATA_TYPE == datatype_name:
                return tclass
        return None


class TextType(DataType):
    DATA_TYPE = 'text'

    def _set_constraints(self, constraints):
        super(TextType, self)._set_constraints(constraints)

    def validate(self, value):
        value = super(TextType, self).validate(value)
        if value is None:
            return value
        if not isinstance(value, str):
            return str(value)
        return value


class NumberType(DataType):
    """Number type.

    Stores a numeric value.
    """
    DATA_TYPE = 'number'

    def _set_constraints(self, constraints):
        super(NumberType, self)._set_constraints(constraints)

    def validate(self, value):
        value = super(NumberType, self).validate(value)
        if value is None:
            return value
        if isinstance(value, str):
            result = float(value)
            return result
        elif isinstance(value, (float, int)):
            return float(value)
        raise ValueError()


class DateType(DataType):
    """Date type.

    Stored as UTC timestamp.
    """
    DATA_TYPE = 'date'
    DATE_FORMAT = '%Y-%m-%d'

    def _set_constraints(self, constraints):
        super(DateType, self)._set_constraints(constraints)
        if 'format' in self.constraints:
            date_format = self.constraints['format']
            if date_format == 'timestamp':
                self.format = None
            else:
                self.format = date_format
        else:
            self.format = self.DATE_FORMAT

    def validate(self, value):
        value = super(DateType, self).validate(value)
        if value is None:
            return value
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return date(value.year, value.month, value.day)
        if self.format:
            if not isinstance(value, str):
                raise ValueError('Expected string')
            return datetime.strptime(value, self.format).date()
        else:
            if not isinstance(value, int) and not isinstance(value, float):
                raise ValueError('Non valid timestamp {}'.format(value))
            return datetime.utcfromtimestamp(value).date()
        raise ValueError()


class EnumType(DataType):
    """Enum type.

    Constraint must provide the allowed 'options' to check in the
    validation step.
    """
    DATA_TYPE = 'enum'

    def _set_constraints(self, constraints):
        if not 'options' in constraints:
            raise ValueError('No options for enum defined')
        self.options = [str(opt) for opt in constraints['options']]
        super(EnumType, self)._set_constraints(constraints)

    def validate(self, value):
        value = super(EnumType, self).validate(value)
        if value is None:
            return value
        for opt in self.options:
            if value == opt:
                return value
        raise ValueError('Non valid option: {}'.format(value))


class ModelDefinition(object):
    def __init__(self, name, fields, uid=None):
        # check that we are receiving valid types
        self.name = name
        self.uid = uid
        for fdef in fields:
            if not issubclass(fdef.__class__, DataType):
                raise ValueError('Non valid type : {}'.format(fdef.__class__))
        self.fields = fields
