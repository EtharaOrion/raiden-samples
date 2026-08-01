import json


import json
import base64


def test_workflow_duplicate_alias_fails(cli, kms, tmp_path):
    r = cli("kms", "create-key")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    alias = "alias/dup-alias-%s" % key_id[:8]
    a = cli("kms", "create-alias", "--alias-name", alias, "--target-key-id", key_id)
    assert a.returncode == 0
    a2 = cli("kms", "create-alias", "--alias-name", alias, "--target-key-id", key_id)
    assert a2.returncode != 0
    assert "AlreadyExists" in a2.stderr
