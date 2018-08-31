from __future__ import unicode_literals

from itertools import chain
from django.forms import Select, SelectMultiple, DateInput

try:
    from django.forms import util
except ImportError:
    from django.forms import utils as util

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape, format_html
from django.forms import widgets as dj_widgets
from django.template import Context, loader


class SelectCallback(Select):
    def __init__(self, attrs=None):
        super(Select, self).__init__(attrs)
        self.choices_callback = None

    def render(self, name, value, attrs=None):
        self.choices = list(self.choices_callback())
        return super(SelectCallback, self).render(name, value, attrs)


class SelectCallbackMultiple(SelectCallback, SelectMultiple):
    pass


class DatePickerWidget(DateInput):
    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(DatePickerWidget, self).build_attrs(extra_attrs, **kwargs)
        attrs['class'] = attrs.get('class', '') + ' date-picker'
        attrs['data-date-autoclose'] = 'true'
        attrs['data-date-format'] = self.format.replace('y', 'yy')\
            .replace('Y', 'yyyy')\
            .replace('M', 'mm')\
            .replace('D', 'dd')\
            .replace('%', '')
        return attrs


class Select2AjaxWidget(Select):

    def __init__(self, attrs=None, choices=(), add_empty=False, data_url=None, **kwargs):
        self.add_empty = add_empty
        self.data_url = data_url
        super(Select2AjaxWidget, self).__init__(attrs=attrs, choices=choices)

    def build_attrs(self, *args, **kwargs):
        """
        Set select2's AJAX attributes.
        """
        attrs = super(Select2AjaxWidget, self).build_attrs(*args, **kwargs)
        if 'class' in attrs:
            attrs['class'] += ' select2'
        else:
            attrs['class'] = 'select2'
        if self.add_empty:
            attrs.setdefault('data-allow-clear', 'true')
        else:
            attrs.setdefault('data-allow-clear', 'false')
        if self.data_url:
            attrs.setdefault('data-ajax--url', self.data_url)
        attrs.setdefault('data-ajax--cache', 'false')
        attrs.setdefault('data-ajax--type', 'GET')
        attrs.setdefault('data-minimum-input-length', 0)
        return attrs


class Select2AjaxMultipleWidget(Select2AjaxWidget, SelectMultiple):
    pass


class LabelWidget(Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''

        final_attrs = self.build_attrs(attrs, name=name)
        id_ = final_attrs.get('id', '')

        label_attrs = self.build_attrs(
            {'id': '%s_label' % id_,
             'class': 'label_widger'},
            **final_attrs)

        out_str = format_html('<span{0}>', util.flatatt(label_attrs))

        if len(self.choices) > 0:
            for option_value, option_label in chain(self.choices, choices):
                if option_value == value:
                    out_str += util.format_html('<span>{0}</span>', option_label)
        else:
            out_str += conditional_escape(util.force_text(value))

        out_str += mark_safe('</span>')

        input_attrs = self.build_attrs(
            {'type': 'hidden',
             'value': util.force_text(value)},
            **final_attrs)

        out_str += util.format_html('<input{0} />', util.flatatt(input_attrs))
        return out_str


if hasattr(dj_widgets, 'RadioFieldRenderer'):
    class RadioFieldRendererTemplated(dj_widgets.RadioFieldRenderer):
        def render(self):
            c = Context({'render': self})
            t = loader.get_template('sdh/forms/radio.html')
            return t.render(c)


    class RadioSelectTemplated(dj_widgets.RadioSelect):
        renderer = RadioFieldRendererTemplated
else:

    class RadioSelectTemplated(dj_widgets.RadioSelect):
        template = 'sdh/forms/radio.html'
