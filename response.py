from http import HTTPStatus


class Response:
    def __init__(self, status_code="404 Not Found", text="Route Doesn't Exists") -> None:
        self.status_code = status_code
        self.text = text
        self.headers = []

    def _normalize_status(self, status_code):
        if isinstance(status_code, HTTPStatus):
            return f"{status_code.value} {status_code.phrase}"

        if isinstance(status_code, int):
            try:
                http_status = HTTPStatus(status_code)
                return f"{http_status.value} {http_status.phrase}"
            except ValueError:
                return str(status_code)

        if isinstance(status_code, str):
            trimmed_status = status_code.strip()
            if trimmed_status.isdigit():
                return self._normalize_status(int(trimmed_status))
            return trimmed_status

        return str(status_code)

    def send(self, text="", status_code="200 OK"):
        if isinstance(text, str):
            self.text = text
        else:
            self.text = str(text)

        self.status_code = self._normalize_status(status_code)

    def as_wsgi(self, start_response):
        body = self.text.encode()
        headers = list(self.headers)

        if not any(header_name.lower() == "content-type" for header_name, _ in headers):
            headers.append(("Content-Type", "text/plain; charset=utf-8"))

        if not any(header_name.lower() == "content-length" for header_name, _ in headers):
            headers.append(("Content-Length", str(len(body))))

        start_response(self.status_code, headers=headers)
        return body