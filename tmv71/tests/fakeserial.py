import io


class FakeSerialPort:
    ports = {}

    @classmethod
    def register(cls, port):
        cls.ports[port.name] = port

    def __new__(cls, port, **kwargs):
        return cls.ports.get(port,
                             super().__new__(cls))

    def __init__(self, port, register=False, **kwargs):
        if hasattr(self, 'name'):
            return

        self.name = port
        self.rx = io.BytesIO()
        self.tx = io.BytesIO()
        self.exc = None

        if register:
            self.ports[self.name] = self

    def raise_next_read(self, exc):
        self.exc = exc

    def stuff(self, data):
        pos = self.tx.tell()
        self.tx.seek(0, 2)
        self.tx.write(data)
        self.tx.seek(pos)

    def read(self, size=1):
        if self.exc is not None:
            exc = self.exc
            self.exc = None
            raise exc()

        data = self.tx.read(size)
        return data

    def read_until(self, terminator=b'\n', size=None):
        acc = []
        while True:
            res = self.read()
            acc.append(res)
            if res == terminator or (size is not None and len(acc) >= size):
                break

        return b''.join(acc)

    def write(self, data):
        return self.rx.write(data)

    def clear(self):
        self.rx.truncate(0)
        self.tx.truncate(0)
        self.tx.seek(0)
        self.rx.seek(0)
