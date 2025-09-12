from repositories.implementations.openai_repo import OpenAIRepo


class _FakeChoice:
    def __init__(self, content: str):
        class _Msg:
            def __init__(self, content: str):
                self.content = content
        self.message = _Msg(content)


class _FakeCompletion:
    def __init__(self, content: str):
        self.choices = [_FakeChoice(content)]


class _FakeClient:
    def __init__(self, content: str = "hi"):
        class _Chat:
            class _Completions:
                def __init__(self, outer: "_FakeClient"):
                    self._outer = outer

                def create(self, **kwargs):
                    return _FakeCompletion(self._outer._content)

            def __init__(self, outer: "_FakeClient"):
                self.completions = _Chat._Completions(outer)

        self.chat = _Chat(self)
        self._content = content


def test_openai_repo_with_injected_client():
    fake = _FakeClient("ok")
    repo = OpenAIRepo(client=fake)
    out = repo.chat([
        {"role": "system", "content": "test"},
        {"role": "user", "content": "hello"},
    ])
    assert out == "ok"
