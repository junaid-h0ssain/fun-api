class Response:
    def __init__(self, status_code="404 Not Found", text="Route Doesn't Exists") -> None:
        self.status_code = status_code
        self.text = text
        self.headers = []

    def send(self, text, status_code):
        if isinstance(text,str):
            self.text = text
        else:
            self.text = str(text)
        self.status_code = status_code