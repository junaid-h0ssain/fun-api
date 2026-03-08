from collections import defaultdict


class Request:
    def __init__(self, environ) -> None:
        self.environ = environ
        self.queries = defaultdict()
        for key, value in self.environ.items():
            setattr(self, key.lower(), value)

        if self.query_string:
            request_queries = self.query_string.split("&")
            for query in request_queries:
                q_key, q_value = query.split("=")
                self.queries[q_key] = q_value