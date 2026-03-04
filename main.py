


import types
from typing import Any
from response import Response
from parse import parse


class FunAPI:
    def __init__(self, middleware: list = []) -> None:
        self.routes = dict()
        self.middleware = middleware
        self.routes_middleware = dict()

    def __call__(self, environ, start_response):
        response = Response()

        for m in self.middleware:
            if isinstance(m, types.FunctionType):
                m(response)

        for path, handlerDict in self.routes.items():
            res = parse(path, environ["PATH_INFO"])

            for requestMethod, handler in handlerDict.items():
                if res and requestMethod == environ["REQUEST_METHOD"]:
                    
                    route_mw_list = self.routes_middleware[path][requestMethod]
                    for m in route_mw_list:
                        if isinstance(m, types.FunctionType):
                            m(response)

                    handler(environ, response, **res.named)
                    response.as_wsgi(start_response)
                    return [response.text.encode()]
        
        response.as_wsgi(start_response)
        return [response.text.encode()]
                
    def common_handler(self, path=None, method=None, middleware=[]):
        def wrapper(handler):
            pathName = path or f"/{handler.__name__}"

            if pathName not in self.routes: 
                self.routes[pathName] = {}

            self.routes[pathName][method] = handler

            if pathName not in self.routes_middleware:
                self.routes_middleware[pathName] = {}

            self.routes_middleware[pathName][method] = middleware
            
            print(self.routes)

        return wrapper
                


    def get(self, path=None, middleware=[]):
        return self.common_handler(path=path, method="GET", middleware=middleware)
    
    def post(self, path=None, middleware=[]):
        return self.common_handler(path=path, method="POST", middleware=middleware)
    
    def put(self, path=None, middleware=[]):
        return self.common_handler(path=path, method="PUT", middleware=middleware)
    
    def delete(self, path=None, middleware=[]):
        return self.common_handler(path=path, method="DELETE", middleware=middleware)
            

    def routes(self, path=None,middleware=[]):
        def wrapper(handler):
            if isinstance(handler, type):
                pathName = path or f"/{handler.__name__.lower()}"
                methods = ["GET", "POST", "PUT", "DELETE"]

                for method in methods:
                    if hasattr(handler, method.lower()):
                        method_handler = getattr(handler, method.lower())
                        self.common_handler(path=pathName, method=method, middleware=middleware)(method_handler)

        return wrapper            