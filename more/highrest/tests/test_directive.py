from more.highrest import HighRestApp, ItemBase, CollectionBase

from webtest import TestApp as Client


class Database(object):
    id_counter = 0

    def __init__(self):
        self.items = []

    def add(self, data):
        id = self.id_counter
        self.items.append(Item(self, id, **data))
        self.id_counter += 1

    def get(self, id):
        try:
            return self.items[id]
        except IndexError:
            return None

    def clear(self):
        self.id_counter = 0
        self.items = []


database = Database()


def setup_function(function):
    database.clear()


class Item(ItemBase):
    def __init__(self, collection, id, title):
        self.collection = collection
        self.id = id
        self.title = title

    def update(self, data):
        self.title = data['title']

    def remove(self):
        self.collection.items[self.id] = None


class Collection(CollectionBase):
    def __init__(self, offset, limit):
        self.offset = offset
        self.limit = limit

    def clone(self, limit, offset):
        return Collection(limit, offset)

    def add(self, data):
        database.add(data)

    def query(self):
        return database.items[self.offset:self.offset + self.limit]

    @staticmethod
    def load(request):
        return {'title': request.json['title']}

    def count(self):
        return len(database.items)


def test_basic_cases():
    class App(HighRestApp):
        pass

    @App.collection(path='/collection', collection=Collection)
    def get_collection(offset=0, limit=10):
        return Collection(offset, limit)

    @App.item(path='/collection/{id}', model=Item, collection=Collection)
    def get_item(id=0):
        return database.get(id)

    @App.json(model=Item)
    def item_get(self, request):
        return {'id': self.id, 'title': self.title}

    App.commit()
    client = Client(App())

    r = client.get('/collection')

    assert r.json == {
        'results': [],
        'next': None,
        'previous': None,
        'count': 0
    }

    r = client.post_json('/collection', {'title': "hello world"}, status=201)

    assert r.json == {
        'results': [{'id': 0, 'title': "hello world"}],
        'next': None,
        'previous': None,
        'count': 1
    }

    r = client.get('/collection/0')
    assert r.json == {'id': 0, 'title': 'hello world'}

    r = client.put_json('/collection/0', {'title': 'bye world'})
    assert r.json == {'id': 0, 'title': 'bye world'}

    r = client.delete('/collection/0', status=204)


def test_batching():
    class App(HighRestApp):
        pass

    for i in range(10):
        database.add({'title': "Title %s" % i})

    @App.collection(path='/collection', collection=Collection)
    def get_collection(offset=0, limit=2):
        return Collection(offset, limit)

    @App.item(path='/collection/{id}', model=Item, collection=Collection)
    def get_item(id=0):
        return database.get(id)

    @App.json(model=Item)
    def item_get(self, request):
        return {'id': self.id, 'title': self.title}

    App.commit()
    client = Client(App())

    r = client.get('/collection')

    # note that to make these tests consistently succeed you
    # need Morepath 0.19+
    assert r.json == {
        'results': [{'id': 0, 'title': "Title 0"},
                    {'id': 1, 'title': "Title 1"}],
        'next': 'http://localhost/collection?limit=2&offset=2',
        'previous': None,
        'count': 10
    }

    r = client.get('/collection?offset=2')

    assert r.json == {
        'results': [{'id': 2, 'title': "Title 2"},
                    {'id': 3, 'title': "Title 3"}],
        'next': 'http://localhost/collection?limit=2&offset=4',
        'previous': 'http://localhost/collection?limit=2&offset=0',
        'count': 10
    }

    r = client.get('/collection?offset=8')

    assert r.json == {
        'results': [{'id': 8, 'title': "Title 8"},
                    {'id': 9, 'title': "Title 9"}],
        'next': None,
        'previous': 'http://localhost/collection?limit=2&offset=6',
        'count': 10
    }
