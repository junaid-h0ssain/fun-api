def app(environ, start_response):
    print(environ)
    start_response("200 OK", headers=[])
    return [b"Hello World"]
