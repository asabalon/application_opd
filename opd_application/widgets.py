from html.parser import HTMLParser
from crispy_forms.layout import BaseInput
from django.forms.widgets import Widget
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class SubmitButton(BaseInput):
    input_type = 'submit'

    def __init__(self, *args, **kwargs):
        self.field_classes = 'btn'
        super(SubmitButton, self).__init__(*args, **kwargs)


class SelectedOptionHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'select':
            for attr in attrs:
                if attr[0] == 'id':
                    self.data['select_id'] = attr[1]

        if tag == 'option':
            for attr in attrs:
                if attr[0] == 'selected':
                    for value_attr in attrs:
                        if value_attr[0] == 'value':
                            self.data['selected_value'] = value_attr[1]


class CustomPhoneNumberPrefixWidget(PhoneNumberPrefixWidget):
    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), returns a Unicode string
        representing the HTML for the whole lot.

        This hook allows you to format the HTML design of the widgets, if
        needed.
        """

        select_widget = SelectedOptionHtmlParser()
        select_widget.feed(rendered_widgets[0])
        return u"""
            <div class="container-fluid">
                <div class="row">
                    <div class="col-xs-4">
                        %s
                    </div>
                    <div class="input-group col-xs-8">
                        <span class="input-group-addon" id="area_code_prefix">%s</span>
                        %s
                    </div>
                </div>
            </div>
            <script type="text/javascript">
                document.getElementById("%s").onchange = function() {changeAreaCodePrefix(this.id, 'area_code_prefix');}
             </script>
            """ % \
               (rendered_widgets[0], select_widget.data['selected_value'], rendered_widgets[1],
                select_widget.data['select_id'])


class FixedInputWidget(Widget):
    def render(self, name, value, attrs=None):
        return u"""
            <h5>
            <input class="col-xs-12" name="%s" value="%s" style="background:none; border:none;" readonly="readonly">
            </input>
            </h5>
            """ % (name, value)


class NonInputWidget(Widget):
    def render(self, name, value, attrs=None):
        return u""""""
