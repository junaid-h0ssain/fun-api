# FunAPI — Technical Documentation

This document explains the theory behind FunAPI, why the project exists, and how every piece of it works.

---

## Why?

Modern Python frameworks (Flask, FastAPI, Django) are powerful but opaque. A beginner can build apps with them without ever understanding what happens when a request arrives. FunAPI was built to answer the question: *"what does a web framework actually do?"*

The answer is:

1. Receives raw HTTP data from a server
2. Matches the request path to a registered handler function
3. Calls that function with the request context
4. Returns the response back to the server

FunAPI does exactly this — no more, no less.

---

## The WSGI Standard

### What is WSGI?

WSGI (Web Server Gateway Interface, [PEP 3333](https://peps.python.org/pep-3333/)) is the standard interface between Python web applications and web servers. It decouples your application logic from the server that runs it. A WSGI application is simply a callable that takes two arguments:

```python
application(environ, start_response)
```

| Argument         | Type       | Description                                        |
|------------------|------------|----------------------------------------------------|
| `environ`        | `dict`     | All request data: method, path, headers, body, etc.|
| `start_response` | `callable` | Called once to set the HTTP status and headers      |

The callable must return an **iterable of byte strings** — the response body.

A complete, valid WSGI application:

```python
def app(environ, start_response):
    start_response("200 OK", [])
    return [b"Hello, world!"]
```

That's all a web server like `gunicorn` needs. It handles TCP connections, HTTP parsing, and TLS — your code only deals with the logical layer.

### Why WSGI and not raw sockets?

You *could* build a server from raw TCP sockets using Python's `socket` module. But then you'd have to parse HTTP/1.1 yourself (method, headers, body framing, keep-alive, chunked encoding...). WSGI gives you a clean, already-parsed dictionary. It's the right layer of abstraction for a framework.

### The `environ` dictionary

Key fields FunAPI uses:

| Key                  | Example value     | Meaning                         |
|----------------------|-------------------|---------------------------------|
| `PATH_INFO`          | `/users/42`       | The URL path                    |
| `REQUEST_METHOD`     | `GET`             | The HTTP method                 |
| `CONTENT_TYPE`       | `application/json`| Request body content type       |
| `wsgi.input`         | file-like object  | The raw request body stream     |

---

## Architecture

### The `FunAPI` class (`main.py`)

```
FunAPI
├── routes         dict[path -> dict[method -> handler]]
├── middleware     list[callable]   (global)
└── routes_middleware  dict[path -> dict[method -> list[callable]]]
```

When you call `FunAPI()`, you get an instance that is itself a valid WSGI callable because it implements `__call__(self, environ, start_response)`.

#### Route Registration

The decorator methods (`get`, `post`, `put`, `delete`) all delegate to `common_handler`:

```python
def common_handler(self, path=None, method=None, middleware=[]):
    def wrapper(handler):
        pathName = path or f"/{handler.__name__}"
        self.routes[pathName][method] = handler
        self.routes_middleware[pathName][method] = middleware
    return wrapper
```

- If no `path` is given, the handler's function name becomes the path (e.g. `def get_users` → `/get_users`).
- The route table is a nested dict: `routes["/users"]["GET"] = get_users`.
- Middleware per route is stored in a parallel nested dict.

#### Request Dispatch (`__call__`)

Every HTTP request runs through this method:

```
1. Create a fresh Response object (default: 404)
2. Run all global middleware
3. Iterate over registered routes
   a. Use `parse(path, environ["PATH_INFO"])` to try matching the path
   b. If matched AND the HTTP method matches:
      - Run route-level middleware
      - Call the handler(environ, response, **url_params)
      - Finalise the response via start_response
      - Return the body as [bytes]
4. If no route matched, return the default 404 response
```

The `parse` library handles parameterised paths like `/users/{id}`. It returns `None` on no match, or a result object with a `.named` dict (e.g. `{"id": "42"}`) on success. These named captures are unpacked as keyword arguments into the handler.

---

### The `Response` class (`response.py`)

`Response` is a thin wrapper that holds the three things a WSGI response needs:

| Attribute      | Default             | Meaning                         |
|----------------|---------------------|---------------------------------|
| `status_code`  | `"404 Not Found"`   | HTTP status line                |
| `text`         | `"Route Doesn't Exists"` | Response body               |
| `headers`      | `[]`                | List of `(name, value)` tuples  |

The `send(text, status_code)` method lets handlers set those values. The `as_wsgi(start_response)` method calls `start_response` with the status and headers, completing the WSGI protocol handshake before the body is returned.

Why separate `send` from `as_wsgi`? So middleware can modify the response object after the handler sets values but before it's committed to the client.

---

### Middleware Design

Middleware in FunAPI is a plain function with the signature:

```python
def my_middleware(res: Response) -> None:
    ...
```

It receives only the response object (not the request). This is intentional for simplicity — middleware here is designed for response mutation (setting headers, logging, etc.) rather than request interception.

**Execution order for a matched route:**

```
Global middleware[0]
Global middleware[1]
...
Route middleware[0]
Route middleware[1]
...
Handler
```

Global middleware runs on every request regardless of path. Route middleware runs only when its specific route is matched.

---

### URL Parameter Parsing

FunAPI delegates path matching to the [`parse`](https://pypi.org/project/parse/) library, which is the inverse of Python's `str.format()`:

```python
from parse import parse

result = parse("/users/{id}", "/users/42")
# result.named == {"id": "42"}
```

This means path templates follow Python format-string syntax. You can also use typed patterns:

```
/users/{id:d}   → id will be parsed as an integer
/files/{name}   → name is a plain string
```

These extracted values are passed directly to the handler via `**res.named`, so the handler signature must include the matching parameter names.

---

## Request Lifecycle (end to end)

```
Client
  │
  │  HTTP request (TCP)
  ▼
gunicorn
  │
  │  Parses HTTP, builds environ dict, calls app(environ, start_response)
  ▼
FunAPI.__call__(environ, start_response)
  │
  ├─ Creates Response(status="404 Not Found")
  ├─ Runs global middleware
  ├─ Iterates routes:
  │    ├─ parse(route_path, environ["PATH_INFO"]) → match?
  │    └─ environ["REQUEST_METHOD"] == registered method?
  │         ├─ Runs route middleware
  │         ├─ Calls handler(environ, response, **url_params)
  │         └─ response.as_wsgi(start_response)  ← commits status + headers
  │
  └─ Returns [response.text.encode()]  ← body bytes
       │
       ▼
gunicorn sends HTTP response back to client
```

---

## Limitations and Possible Extensions

| Feature                  | Current state      | How to add                                        |
|--------------------------|--------------------|---------------------------------------------------|
| Request body parsing     | Not implemented    | Read `environ["wsgi.input"]`, parse JSON/form data |
| Response headers         | Empty list         | Add methods like `res.set_header(name, value)`     |
| Middleware request access| No access to `req` | Change middleware signature to `(req, res)`        |
| Async support            | No (sync WSGI)     | Switch to ASGI (`scope, receive, send`) + `uvicorn`|
| Error handling           | None               | Add try/except in `__call__`, return 500 response  |
| Class-based routing      | Partially sketched | Complete the `routes` decorator in `main.py`       |
| Static files             | None               | Check path prefix, read file, return bytes         |
