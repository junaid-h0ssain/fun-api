
class FunAPI:
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        print(environ)
        start_response("200 OK", headers=[])
        return[b"Hello, World."]
    


funapi = FunAPI()
