import factory

from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.LazyAttribute(
        lambda o: "%s.%s" % (o.first_name.lower(), o.last_name.lower())
    )
    email = factory.Faker("email")
    password = factory.Faker("word")
    is_staff = False
    is_active = True
