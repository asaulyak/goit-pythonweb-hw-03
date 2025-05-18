import datetime
import json
import mimetypes
import pathlib
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("."))
template = env.get_template("messages.html")
storage_path = "./storage/data.json"


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message.html":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.send_messages()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        self.store_to_json(data_dict)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def send_messages(self):
        with open(storage_path, "r") as file:
            content = json.load(file)
            messages = [value for key, value in content.items()]
            output = template.render(
                messages=messages,
            )

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(output.encode("ascii"))

    def store_to_json(self, data):
        content = {}
        with open(storage_path, "r") as file:
            content = json.load(file)
            ts = time.time()
            key = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S:%f")

            content[key] = data

        with open(storage_path, "w") as file_output:
            json.dump(content, file_output, indent=2)


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
