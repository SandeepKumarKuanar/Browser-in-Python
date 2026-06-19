import socket
import ssl


class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme == ["http", "https"]

        if "/" not in url:
            url += "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        ## adding a custom port support to the already made HTTPS support
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

    def request(self):
        s = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
        # We decide the port based on the scheme
        s.connect((self.host, self.port))
        # if it's a HTTPS request, we make it secure
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        request = f"GET {self.path} HTTP/1.0\r\n"
        request += f"Host: {self.host}\r\n"
        request += "\r\n"
        s.send(request.encode("utf8"))
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        # store all of the headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        ## returning the mess till now
        content = response.read()
        s.close()
        return content


def show(body: str) -> None:
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")


def load(url: URL) -> None:
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys

    load(URL(sys.argv[1]))
