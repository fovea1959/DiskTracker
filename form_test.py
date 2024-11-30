from datetime import datetime

from werkzeug.datastructures import MultiDict

from wtforms import Form, validators
from wtforms.fields.simple import PasswordField, BooleanField
from wtforms_components import DateTimeField, DateRange, StringField


class TestForm(Form):
    date_field = DateTimeField(
        'Date',
        validators=[DateRange(
            min=datetime(2000, 1, 1),
            max=datetime(2000, 10, 10)
        )]
    )


def main():
    f = TestForm(MultiDict([('date_field', '2000-02-02 10:00:00')]))
    f.validate()
    print(f.errors)
    print(f.date_field)
    print(f.data)



if __name__ == '__main__':
    main()
