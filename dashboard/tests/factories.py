import factory
from dashboard.models import CourseModel, ClassModel

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseModel

    course_name = factory.Sequence(lambda n: f'Curso de prueba {n}')
    description = factory.Faker('text')
    category = factory.Faker('word')
    level = factory.Iterator(['Principiante', 'Intermedio', 'Avanzado'])
    bullet_points = factory.List([
        factory.Faker('sentence') for _ in range(3)
    ])

class ClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassModel

    class_name = factory.Sequence(lambda n: f'Clase de prueba {n}')
    description = factory.Faker('text')
    course = factory.SubFactory(CourseFactory)
    bullet_points = factory.List([
        factory.Faker('sentence') for _ in range(3)
    ]) 