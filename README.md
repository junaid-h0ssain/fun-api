# FunAPI

A minimal, decorator-based Python web framework built on top of the WSGI standard — written from scratch to understand how frameworks like Flask actually work under the hood.

---

## What is it?

FunAPI is a lightweight HTTP routing framework. You define routes using simple decorators, attach middleware, and serve it with any WSGI-compatible server (e.g. `gunicorn`). No magic, no heavy dependencies — just Python and the WSGI interface.

---

## Requirements

- Python >= 3.14
- [`gunicorn`](https://gunicorn.org/) — WSGI server
- [`parse`](https://pypi.org/project/parse/) — URL pattern matching

Install dependencies with:

```bash
pip install gunicorn parse
```

Or if you're using `uv` / `pyproject.toml`:

```bash
uv sync
```

---

## Quick Start

```python
from main import FunAPI

app = FunAPI()

@app.get("/hello")
def hello(req, res):
    res.send("Hello, world!", "200 OK")
```

Run it with gunicorn:

```bash
gunicorn exp:funapi
```

Then visit `http://127.0.0.1:8000/hello`.

---

## Routing

FunAPI supports the four main HTTP methods via decorators:

```python
@app.get("/users")
def list_users(req, res):
    res.send("List of users", "200 OK")

@app.post("/users")
def create_user(req, res):
    res.send("User created", "201")

@app.put("/users")
def update_user(req, res):
    res.send("User updated", "200 OK")

@app.delete("/users")
def delete_user(req, res):
    res.send("User deleted", "200 OK")
```

### URL Parameters

Use `{param}` syntax in the path. The parameter is passed as a keyword argument to the handler:

```python
@app.get("/users/{id}")
def get_user(req, res, id):
    res.send(f"User ID: {id}", "200 OK")
```

---

## Middleware

### Global Middleware

Runs on every request:

```python
def log_request(res):
    print("Incoming request")

app = FunAPI(middleware=[log_request])
```

### Route-Level Middleware

Runs only for a specific route:

```python
def auth_check(res):
    print("Checking auth...")

@app.get("/admin", middleware=[auth_check])
def admin(req, res):
    res.send("Admin panel", "200 OK")
```

---

## Project Structure

```
fun-api/
├── main.py        # FunAPI class — core routing and WSGI logic
├── response.py    # Response class — wraps WSGI start_response
├── exp.py         # Example app demonstrating usage
└── pyproject.toml
```

---
