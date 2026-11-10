"""Preview the static export with its response headers: python3 extract/serve.py."""

import argparse
from fnmatch import fnmatchcase
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

from publish import OUTPUT, publish


def header_rules():
    rules = []
    for line in (OUTPUT / "_headers").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            rules.append((line.strip(), {}))
        else:
            key, value = line.strip().split(":", 1)
            rules[-1][1][key] = value.strip()
    return rules


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUTPUT), **kwargs)

    def end_headers(self):
        path = unquote(urlsplit(self.path).path)
        for pattern, headers in header_rules():
            if fnmatchcase(path, pattern):
                for name, value in headers.items():
                    self.send_header(name, value)
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404)
        return None

    def send_error(self, code, message=None, explain=None):
        if code != 404:
            return super().send_error(code, message, explain)
        body = (OUTPUT / "404.html").read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_head(self):
        path = unquote(urlsplit(self.path).path)
        if any(part.startswith((".", "_")) for part in path.split("/") if part):
            self.send_error(404)
            return None
        for line in (OUTPUT / "_redirects").read_text().splitlines():
            source, target, status = line.split()
            if path == source:
                self.send_response(int(status))
                self.send_header("Location", target)
                self.end_headers()
                return None
        return super().send_head()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    publish()
    print(f"Serving {OUTPUT} at http://127.0.0.1:{args.port}/", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
