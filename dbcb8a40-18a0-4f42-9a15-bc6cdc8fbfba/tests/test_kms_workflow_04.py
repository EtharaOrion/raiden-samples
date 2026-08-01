import json


import json
import base64


def test_workflow_alias_describe(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "alias-describe")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    aname = "alias/ad-" + key_id[:8]
    ca = cli("kms", "create-alias", "--alias-name", aname, "--target-key-id", key_id)
    assert ca.returncode == 0
    d = cli("kms", "describe-key", "--key-id", aname)
    assert d.returncode == 0
    dmeta = json.loads(d.stdout)["KeyMetadata"]
    assert dmeta["KeyId"] == key_id
