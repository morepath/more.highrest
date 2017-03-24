import dectate
from morepath.directive import JsonAction, PathCompositeAction


class CollectionAction(dectate.Composite):
    def __init__(self, path, collection):
        self.path = path
        self.collection = collection

    def actions(self, obj):
        # FIXME: permission

        # collection path
        # FIXME: other path parameters such as variables, converters, etc
        yield PathCompositeAction(model=self.collection, path=self.path), obj

        # GET collection
        # FIXME: next, previous, count, page nr
        def collection_get(self, request):
            return {
                'results': [request.view(item) for item in self.query()],
                'next': request.link(self.next()),
                'previous': request.link(self.previous()),
                'count': self.count()
            }

        yield JsonAction(model=self.collection,
                         permission=None), collection_get

        # POST collection
        def collection_post(self, request, data):
            self.add(data)

            @request.after
            def set_status(request):
                request.status = 201
            return request.view(self)
        yield JsonAction(model=self.collection, load=self.collection.load,
                         request_method='POST',
                         permission=None), collection_post


class ItemAction(dectate.Composite):
    def __init__(self, path, model, collection):
        self.path = path
        self.model = model
        self.collection = collection

    def actions(self, obj):
        # FIXME: permission

        yield PathCompositeAction(model=self.model,
                                  path=self.path), obj

        # DELETE item
        def item_delete(self, request):
            @request.after
            def set_status(request):
                request.status = 204
                del request.headers['Content-Type']
            self.remove()

        yield JsonAction(model=self.model, request_method='DELETE',
                         permission=None), item_delete

        # PUT item
        def item_put(self, request, data):
            self.update(data)
            return request.view(self)

        yield JsonAction(model=self.model, load=self.collection.load,
                         request_method='PUT', permission=None), item_put
