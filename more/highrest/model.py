class CollectionBase(object):
    def clone(self, offset, limit, *args, **kw):
        raise NotImplementedError()

    def add(self, data):
        raise NotImplementedError()

    def query(self):
        raise NotImplementedError()

    @staticmethod
    def load(request):
        raise NotImplementedError()

    def count(self):
        raise NotImplementedError()

    def previous(self):
        if self.offset == 0:
            return None
        offset = self.offset - self.limit
        if offset < 0:
            offset = 0
        return self.clone(offset, self.limit)

    def next(self):
        if self.offset + self.limit >= self.count():
            return None
        offset = self.offset + self.limit
        return self.clone(offset, self.limit)


class ItemBase(object):
    def update(self, data):
        raise NotImplementedError()

    def remove(self):
        raise NotImplementedError()
