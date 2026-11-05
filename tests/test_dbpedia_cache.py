import subprocess
import sys

import scripts.get_evidence as ge


def test_dbpedia_query_uses_timeout_and_cache(tmp_path, monkeypatch):
    ge.CACHE_DIR = str(tmp_path)
    seen = {}

    class DummySPARQL:
        def __init__(self, endpoint):
            self.endpoint = endpoint

        def setTimeout(self, value):
            seen["timeout"] = value

        def setQuery(self, query):
            seen["query"] = query

        def setReturnFormat(self, value):
            seen["format"] = value

        def query(self):
            raise TimeoutError("simulated DBpedia timeout")

    monkeypatch.setattr(ge, "SPARQLWrapper", DummySPARQL)

    result = ge._execute_sparql_query("SELECT ?s WHERE { ?s ?p ?o . }")
    assert result == []
    assert seen["timeout"] == 10
    assert "SELECT ?s WHERE" in seen["query"]


def test_dbpedia_query_timeout_is_enforced():
    code = """
import time
import scripts.get_evidence as ge

class DummySPARQL:
    def __init__(self, endpoint):
        self.endpoint = endpoint
    def setTimeout(self, value):
        pass
    def setQuery(self, query):
        pass
    def setReturnFormat(self, value):
        pass
    def query(self):
        time.sleep(30)
        return {"results": {"bindings": []}}

ge.SPARQLWrapper = DummySPARQL
print(ge._execute_sparql_query("SELECT ?s WHERE { ?s ?p ?o . }"))
"""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=15,
        cwd="C:/Users/sanch/expclaim",
    )
    assert proc.returncode == 0
    assert "[]" in proc.stdout
