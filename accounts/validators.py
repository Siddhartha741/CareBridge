import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("Password must contain at least 1 uppercase letter."))
        if not re.search(r'[0-9]', password):
            raise ValidationError(_("Password must contain at least 1 number."))
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(_("Password must contain at least 1 special character."))

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter, 1 number, and 1 special character.")