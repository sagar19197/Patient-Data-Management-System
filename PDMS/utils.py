from django.contrib.auth.tokens import PasswordResetTokenGenerator

class Generator(PasswordResetTokenGenerator):
    def _make_hash_value(self, u, timestamp):
        return str(u.pk) + str(timestamp)
maketoken=Generator()