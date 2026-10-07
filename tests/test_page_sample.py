import json

from tests import make_sample


def test_sample_is_fresh():
    on_disk = json.loads(make_sample.SAMPLE.read_text(encoding="utf-8"))
    assert on_disk == make_sample.build(), "Sample is stale: run python -m tests.make_sample"
