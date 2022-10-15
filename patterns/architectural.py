from threading import local


class UnitOfWork:
    current = local()

    def __init__(self):
        self.create_objects = []
        self.update_objects = []
        self.delete_objects = []

    def set_mapper_registry(self, MapperRegistry):
        self.MapperRegistry = MapperRegistry

    def add_create(self, obj):
        self.create_objects.append(obj)

    def add_update(self, obj):
        self.update_objects.append(obj)

    def add_delete(self, obj):
        self.delete_objects.append(obj)

    def commit(self):
        self.create()
        self.update()
        self.delete()

        self.create_objects.clear()
        self.update_objects.clear()
        self.delete_objects.clear()

    def create(self):
        for obj in self.create_objects:
            self.MapperRegistry.get_mapper(obj).create(obj)

    def update(self):
        for obj in self.update_objects:
            self.MapperRegistry.get_mapper(obj).update(obj)

    def delete(self):
        for obj in self.delete_objects:
            self.MapperRegistry.get_mapper(obj).delete(obj)

    @staticmethod
    def new_current():
        __class__.set_current(UnitOfWork())

    @classmethod
    def set_current(cls, unit_of_work):
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls):
        return cls.current.unit_of_work


class DomainObject:

    def mark_create(self):
        UnitOfWork.get_current().add_create(self)

    def mark_update(self):
        UnitOfWork.get_current().add_update(self)

    def mark_delete(self):
        UnitOfWork.get_current().add_delete(self)
