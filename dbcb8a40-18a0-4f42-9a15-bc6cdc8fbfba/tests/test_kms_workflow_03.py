import json


import json
import base64


def test_workflow_create_alias_listaliases(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "aliased")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    aname = "alias/wf-" + key_id[:8]
    ca = cli("kms", "create-alias", "--alias-name", aname, "--target-key-id", key_id)
    assert ca.returncode == 0
    la = cli("kms", "list-aliases")
    assert la.returncode == 0
    aliases = json.loads(la.stdout)["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert aname in names
