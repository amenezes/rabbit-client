PAYLOAD = {"paginas": ["ABC", "123"], "documento": 123, "descricao": "abc"}


class EngineMock:
    def connect(self, *args, **kwargs):
        pass


def create_engine_mock(*args, **kwargs):
    return EngineMock()


def test_configure(monkeypatch):
    pass


def test_exec():
    pass


def test_save():
    pass


def test_get_oldest_event():
    pass
