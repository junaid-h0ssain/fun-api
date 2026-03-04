



class FunAPI:
    def __init__(self):
        self.routes = dict()

    def __call__(self, environ, start_response):
        response = {}
        for path, handlerDict in self.routes.items():
            for requestMethod, handler in handlerDict.items():
                if path == environ["PATH_INFO"] and requestMethod == environ["REQUEST_METHOD"]:
                    handler(environ, response)
                    start_response(response['status_code'], headers=response['headers'])
                    return [response['text'].encode()]
                


    def get(self, path=None):
        def wrapper(handler):
            pathName = path or f"/{handler.__name__}"

            if pathName not in self.routes: 
                self.routes[pathName] = {}

            self.routes[pathName]["GET"] = handler
            
            print(self.routes)

        return wrapper