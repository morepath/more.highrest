from more.highrest import HighRestApp

from webtest import TestApp as Client


def test_root():
    class App(HighRestApp):
        pass

    class Item(object):
        def __init__(self, id, title):
            self.id = id
            self.title = title

    class Collection(object):
        model = Item

        id_counter = 0

        def __init__(self):
            self.items = []

        def add(self, data):
            id = self.id_counter
            self.items.append(Item(id, **data))
            self.id_counter += 1

        def query(self):
            return self.items

        def get(self, id):
            # FIXME: this conversion should be configurable
            id = int(id)
            try:
                return self.items[id]
            except IndexError:
                return None

        def update(self, item, data):
            item.title = data['title']

        def remove(self, item):
            self.items[item.id] = None

    def load_item(request):
        return {'title': request.json['title']}

    def dump_item(item, request):
        return {'id': item.id, 'title': item.title}

    collection = Collection()

    @App.collection(path='/collection',
                    collection=Collection, load=load_item,
                    dump=dump_item)
    def get_collection():
        return collection

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
