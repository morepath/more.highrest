from more.highrest import HighRestApp

from webtest import TestApp as Client


class Item(object):
    def __init__(self, collection, id, title):
        self.collection = collection
        self.id = id
        self.title = title

    def update(self, data):
        self.title = data['title']

    def remove(self):
        self.collection.items[self.id] = None


class Collection(object):
    id_counter = 0

    def __init__(self):
        self.items = []

    def add(self, data):
        id = self.id_counter
        self.items.append(Item(self, id, **data))
        self.id_counter += 1

    def query(self):
        return self.items

    @staticmethod
    def load(request):
        return {'title': request.json['title']}

    def get(self, id):
        try:
            return self.items[id]
        except IndexError:
            return None


def test_basic_cases():
    class App(HighRestApp):
        pass

    collection = Collection()

    @App.collection(path='/collection', collection=Collection)
    def get_collection():
        return collection

    @App.item(path='/collection/{id}', model=Item, collection=Collection)
    def get_item(id=0):
        return collection.get(id)

    @App.json(model=Item)
    def item_get(self, request):
        return {'id': self.id, 'title': self.title}

    App.commit()
    client = Client(App())
    r = client.get('/collection')

    assert r.json == []

    r = client.post_json('/collection', {'title': "hello world"}, status=201)

    assert r.json == [{'id': 0, 'title': "hello world"}]

    r = client.get('/collection/0')
    assert r.json == {'id': 0, 'title': 'hello world'}

    r = client.put_json('/collection/0', {'title': 'bye world'})
    assert r.json == {'id': 0, 'title': 'bye world'}

    r = client.delete('/collection/0', status=204)
