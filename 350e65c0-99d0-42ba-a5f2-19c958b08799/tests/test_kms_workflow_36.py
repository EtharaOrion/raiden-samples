import json


import base64
import json
import uuid


def test_workflow_rpc_create_cli_describe(cli, kms, tmp_path):
    resp = kms.rpc("CreateKey", {"Description": "rpc"})
    kid = resp["KeyMetadata"]["KeyId"]
    d = cli("kms", "describe-key", "--key-id", kid)
    assert d.returncode == 0
    assert json.loads(d.stdout)["KeyMetadata"]["KeyId"] == kid
