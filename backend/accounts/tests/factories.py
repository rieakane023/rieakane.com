import factory

from accounts.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """Real admin users for tests. Use the `make_user` fixture for roles."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    role = User.Role.READONLY
    is_staff = True
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "pass-w0rd-123")
        if create:
            self.save()
