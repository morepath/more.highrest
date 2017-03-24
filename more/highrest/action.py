import dectate
from morepath.directive import JsonAction, PathAction


class CollectionAction(dectate.Composite):
    def __init__(self, path, collection, load, dump):
        self.path = path
        self.collection = collection
        self.load = load
        self.dump = dump

    def actions(self, obj):
        # FIXME: permission

        # collection path
        # FIXME: other path parameters such as variables, converters, etc
        yield PathAction(model=self.collection, path=self.path), obj

        # GET collection
        def collection_get(self, request):
            return [request.view(item) for item in
                    self.query()]
        yield JsonAction(model=self.collection,
                         permission=None), collection_get

        # POST collection
        def collection_post(self, request, data):
            self.add(data)

            @request.after
            def set_status(request):
                request.status = 201
            return request.view(self)
        yield JsonAction(model=self.collection, load=self.load,
                         request_method='POST',
                         permission=None), collection_post

        dump = self.dump

        # item path
        def get_item(self, id):
            return obj().get(id)

        yield PathAction(model=self.collection.model,
                         path=self.path + '/{id}'), get_item

        # GET item
        def item_get(self, request):
            return dump(self, request)

        yield (JsonAction(model=self.collection.model, permission=None),
               item_get)

        # DELETE item
        def item_delete(self, request):
            @request.after
            def set_status(request):
                request.status = 204
                del request.headers['Content-Type']
            obj().remove(self)

        yield JsonAction(model=self.collection.model, request_method='DELETE',
                         permission=None), item_delete

        # PUT item
        def item_put(self, request, data):
            obj().update(self, data)
            return request.view(self)

        yield JsonAction(model=self.collection.model, load=self.load,
                         request_method='PUT', permission=None), item_put
