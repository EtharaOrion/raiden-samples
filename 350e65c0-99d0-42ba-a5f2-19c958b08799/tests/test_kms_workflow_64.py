import json


import base64
import json
import uuid


def test_workflow_describe_keyusage_field(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--key-usage", "ENCRYPT_DECRYPT")
    assert r.returncode == 0
    kid = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    d = cli("kms", "describe-key", "--key-id", kid)
    assert d.returncode == 0
    assert json.loads(d.stdout)["KeyMetadata"]["KeyUsage"] == "ENCRYPT_DECRYPT"
