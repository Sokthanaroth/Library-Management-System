import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SpecialCharacterValidator:
    """
    Validate whether the password contains at least one special character.
    """
    def validate(self, password, user=None):
        if not re.findall(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("The password must contain at least one special character."),
                code='password_no_special',
            )
    
    def get_help_text(self):
        return _("Your password must contain at least one special character.")