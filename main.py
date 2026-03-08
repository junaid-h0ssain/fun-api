
import inspect
import types
from typing import Any
from response import Response
from parse import parse

SUPPORTED_METHODS = {"GET", "POST", "PUT", "DELETE"}

class FunAPI:
    def __init__(self, middleware: list | None = None) -> None:
        self.route_handlers = {}
        self.middleware = middleware or []
        self.routes_middleware = {}

    def __call__(self, environ, start_response):
        response = Response()

        for m in self.middleware:
            if isinstance(m, types.FunctionType):
                m(response)

        for path, handlerDict in self.route_handlers.items():
            res = parse(path, environ["PATH_INFO"])

            for requestMethod, handler in handlerDict.items():
                if res and requestMethod == environ["REQUEST_METHOD"]:
                    
                    route_mw_list = self.routes_middleware[path][requestMethod]
                    for m in route_mw_list:
                        if isinstance(m, types.FunctionType):
                            m(response)

                    handler(environ, response, **res.named)
                    return [response.as_wsgi(start_response)]
        
        return [response.as_wsgi(start_response)]

    def register_route(self, path=None, handler=None, method=None, middleware=None):
        if handler is None or method is None:
            return

        path_name = path or f"/{handler.__name__}"

        if path_name not in self.route_handlers:
            self.route_handlers[path_name] = {}

        self.route_handlers[path_name][method] = handler

        if path_name not in self.routes_middleware:
            self.routes_middleware[path_name] = {}

        self.routes_middleware[path_name][method] = middleware or []

    def common_handler(self, path=None, method=None, middleware=None):
        def wrapper(handler):
            self.register_route(path=path, handler=handler, method=method, middleware=middleware)
            return handler

        return wrapper
                

    def get(self, path=None, middleware=None):
        return self.common_handler(path=path, method="GET", middleware=middleware)
    
    def post(self, path=None, middleware=None):
        return self.common_handler(path=path, method="POST", middleware=middleware)
    
    def put(self, path=None, middleware=None):
        return self.common_handler(path=path, method="PUT", middleware=middleware)
    
    def delete(self, path=None, middleware=None):
        return self.common_handler(path=path, method="DELETE", middleware=middleware)
            

    def routes(self, path=None, middleware=None):
        def wrapper(handler):
            if isinstance(handler, type):
                members = inspect.getmembers(handler, lambda x: inspect.isfunction(x) and not (
                    x.__name__.startswith("__") and x.__name__.endswith("__")
                ) and x.__name__.upper() in SUPPORTED_METHODS)

                for fn_name, fn_handler in members:
                    self.register_route(
                        path=path or f"/{handler.__name__}",
                        handler=fn_handler,
                        method=fn_name.upper(),
                        middleware=middleware,
                    )

            return handler

        return wrapper            