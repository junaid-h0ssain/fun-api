


from typing import Any
from response import Response
from parse import parse


class FunAPI:
    def __init__(self):
        self.routes = dict()

    def __call__(self, environ, start_response):
        response = Response()
        for path, handlerDict in self.routes.items():
            res = parse(path, environ["PATH_INFO"])
            for requestMethod, handler in handlerDict.items():
                if path == environ["PATH_INFO"] and requestMethod == environ["REQUEST_METHOD"]:
                    handler(environ, response)
                    response.as_wsgi(start_response)
                    return [response.text.encode()]
        
        response.as_wsgi(start_response)
        return [response.text.encode()]
                
    def common_handler(self, path=None, method=None):
        def wrapper(handler):
            pathName = path or f"/{handler.__name__}"

            if pathName not in self.routes: 
                self.routes[pathName] = {}

            self.routes[pathName][method] = handler
            
            print(self.routes)

        return wrapper
                


    def get(self, path=None):
        return self.common_handler(path=path, method="GET")
    
    def post(self, path=None):
        return self.common_handler(path=path, method="POST")
    
    def put(self, path=None):
        return self.common_handler(path=path, method="PUT")
    
    def delete(self, path=None):
        return self.common_handler(path=path, method="DELETE")
            