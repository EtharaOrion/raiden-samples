import json


import base64
import json
import uuid


def test_workflow_keyspec_symmetric(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--key-spec", "SYMMETRIC_DEFAULT", "--description", "ks")
    assert r.returncode == 0
    kid = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    d = cli("kms", "describe-key", "--key-id", kid)
    assert d.returncode == 0
    assert json.loads(d.stdout)["KeyMetadata"]["KeyId"] == kid
