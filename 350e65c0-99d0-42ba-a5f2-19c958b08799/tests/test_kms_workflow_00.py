import json


import base64
import json
import uuid


def test_workflow_create_describe(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "d1")
    assert r.returncode == 0
    kid = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    d = cli("kms", "describe-key", "--key-id", kid)
    assert d.returncode == 0
    md = json.loads(d.stdout)["KeyMetadata"]
    assert md["KeyId"] == kid
