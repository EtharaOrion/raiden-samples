import json


import json
import base64


def test_workflow_duplicate_alias_fails(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "dup-alias")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    aname = "alias/dup-" + key_id[:8]
    ca = cli("kms", "create-alias", "--alias-name", aname, "--target-key-id", key_id)
    assert ca.returncode == 0
    ca2 = cli("kms", "create-alias", "--alias-name", aname, "--target-key-id", key_id)
    assert ca2.returncode != 0
    assert "AlreadyExistsException" in (ca2.stderr + ca2.stdout)
