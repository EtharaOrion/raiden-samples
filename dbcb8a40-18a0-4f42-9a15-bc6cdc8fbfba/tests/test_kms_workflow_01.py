import json


import json
import base64


def test_workflow_create_describe(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "desc-test")
    assert r.returncode == 0
    meta = json.loads(r.stdout)["KeyMetadata"]
    key_id = meta["KeyId"]
    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0
    dmeta = json.loads(d.stdout)["KeyMetadata"]
    assert dmeta["KeyId"] == key_id
    assert dmeta["Enabled"] is True
