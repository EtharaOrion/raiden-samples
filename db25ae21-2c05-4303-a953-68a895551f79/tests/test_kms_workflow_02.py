import json


import json
import base64


def test_workflow_create_alias_describe(cli, kms, tmp_path):
    r = cli("kms", "create-key")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    alias = "alias/workflow-alias-%s" % key_id[:8]
    a = cli("kms", "create-alias", "--alias-name", alias, "--target-key-id", key_id)
    assert a.returncode == 0
    d = cli("kms", "describe-key", "--key-id", alias)
    assert d.returncode == 0
    assert json.loads(d.stdout)["KeyMetadata"]["KeyId"] == key_id
