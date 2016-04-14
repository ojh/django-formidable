# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError, ImproperlyConfigured


class PresetsRegister(dict):

    def build_rules(self, form):
        rules = []
        for preset in form.presets.all():
            klass = self[preset.slug]
            instance = klass(preset.arguments.all())
            rules.append(instance)
        return rules


presets_register = PresetsRegister()


class PresetsMetaClass(type):
    """
    Build a new class of Presets.
    Check if all needed attribute are declared inside the class
    (slug, label, description, default_message) and Parameters
    define through MetaParameters inside class.
    Collect all object declared as arguments on put it inside a specific
    dictionary (as declared_field in django form).
    Finally, register the built class with its slug in presets_register.
    """

    def __new__(mcls, name, base, attrs):
        needs = [
            'slug', 'label', 'description', 'default_message', 'MetaParameters'
        ]
        for attr in needs:
            if attr not in attrs:
                raise ValidationError("You need to specify {} in {}".format(
                    attr, name
                ))
            if attrs[attr] is None:
                raise ValidationError(
                    "Do not accept None value for {} in {}".format(attr, name)
                )

        _declared_arguments = {}

        # Separeted the arguments to injected inside a specific dictionary
        for slug, arg in attrs['MetaParameters'].__dict__.items():
            if isinstance(arg, PresetArgument):
                arg.set_slug(slug)
                _declared_arguments[slug] = arg

        attrs['_declared_arguments'] = _declared_arguments
        klass = super(PresetsMetaClass, mcls).__new__(mcls, name, base, attrs)
        if attrs['slug']:
            presets_register[klass.slug] = klass
        return klass


class PresetArgument(object):

    def __init__(self, label, slug=None,
                 help_text='', placeholder='', items=None):
        self.slug = slug
        self.label = label
        self.help_text = help_text
        self.placeholder = placeholder
        self.types = self.get_types()
        self.has_items = items is not None
        self.items = items or {}

    def get_types(self):
        return [self.__class__.type_]

    def set_slug(self, slug):
        """
        Set a slug only if the original slug is no set before
        """
        if self.slug is None:
            self.slug = slug

    def get_value(self, arguments, fields):

        for arg in arguments:
            if arg.slug == self.slug:
                if arg.field_id:
                    return fields[arg.field_id]
                return arg.value

        raise ImproperlyConfigured(
            '{} is missing'.format(self.slug)
        )


class PresetFieldArgument(PresetArgument):

    type_ = 'field'

    def get_reference(self, argument):
        return argument.field_id


class PresetValueArgument(PresetArgument):

    type_ = 'value'

    def get_reference(self, argument):
        return argument.value


class PresetFieldOrValueArgument(PresetArgument):

    def get_types(self):
        return ['field', 'value']

    def get_reference(self, argument):
        if argument.field_id:
            return argument.field_id
        return argument.value


class Presets(object):

    slug = ''
    label = ''
    description = ''
    default_message = ''

    __metaclass__ = PresetsMetaClass

    class MetaParameters:
        pass

    def __init__(self, arguments, message=None):
        self.arguments = arguments
        self.message = message or self.default_message

    def __call__(self, cleaned_data):
        kwargs = self.collect_kwargs(cleaned_data)
        if not self.run(**kwargs):
            raise ValidationError(self.get_message())
        return True

    def collect_kwargs(self, cleaned_data):
        kwargs = {}
        for arg in self._declared_arguments.values():
            kwargs[arg.slug] = arg.get_value(self.arguments, cleaned_data)
        return kwargs

    def get_message_kwargs(self):
        kwargs = {}
        for argument in self.arguments:
            parameter = self._declared_arguments[argument.slug]
            kwargs[argument.slug] = parameter.get_reference(argument)
        return kwargs

    def get_message(self):
        kwargs = self.get_message_kwargs()
        return self.message.format(**kwargs)


class ConfirmationPresets(Presets):

    slug = 'confirmation'
    label = 'Confirmation'
    description = "Be sure two fields are exacly the same value"
    default_message = "{left} are not equals to {right}"

    class MetaParameters:
        left = PresetFieldArgument('Reference', help_text='field to compare')
        right = PresetFieldOrValueArgument(
            'Compare to', help_text='compare with'
        )

    def run(self, left, right):
        return left == right


class ComparisonPresets(Presets):

    slug = 'comparison'
    label = 'comparison'
    description = "Compare two fields with standard operation"
    default_message = "{left} is not {operator} to {right}"

    mapper = {
        'eq': lambda x, y: x == y,
        'neq': lambda x, y: x != y,
        'gt': lambda x, y: x > y,
        'gte': lambda x, y: x >= y,
        'lt': lambda x, y: x < y,
        'lte': lambda x, y: x <= y,
    }

    class MetaParameters:
        left = PresetFieldArgument('Reference')
        operator = PresetValueArgument('Operator', items={
            'eq': '=',  'lt': '<', 'lte': '<=', 'gt': '>',
            'gte': '>=', 'neq': '!='
        })
        right = PresetFieldArgument('Compare to')

    def run(self, left, operator, right):
        meth = self.mapper[operator]
        return meth(left, right)


class RequiredIfNotEmpty(Presets):

    slug = 'required-depends-on-the-value'
    label = 'required if needed'
    description = 'mark a field as required depends another field value'
    default_message = '{reference} is {value}, {field} has to be filled'

    class MetaParameters:
        reference = PresetFieldArgument('reference')
        value = PresetValueArgument('value')
        field = PresetFieldArgument('field')

    def run(self, reference, value, field):
        if reference == value:
            return field is not None
        return True
