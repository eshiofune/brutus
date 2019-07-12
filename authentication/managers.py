import re, string

from django.contrib.auth.models import UserManager


class PersonManager(UserManager):
    def password_valid(self, password):
        if len(password) != 16:
            return False
        
        if len(re.findall(r"[@#$%]", password)) != 2:
            return False

        if len(re.findall(r"[0-9]", password)) != 3:
            return False

        if len(re.findall(r"[a-z]", password)) == 0:
            return False
        
        if not (password[0].isupper() and password[1].isupper()):
            return False

        return True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if self.password_valid(password):
            print(password)
            super().create_user(username, email=email, password=password, **extra_fields)
        else:
            raise Exception("Invalid password")