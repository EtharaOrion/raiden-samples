import json


import json
import base64


def test_workflow_create_describe_state(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "describe-me")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0
    meta = json.loads(d.stdout)["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Enabled"] is True
