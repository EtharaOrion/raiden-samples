import json


import json
import base64


def test_workflow_disable_then_encrypt_fails(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "to-disable")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    dis = cli("kms", "disable-key", "--key-id", key_id)
    assert dis.returncode == 0
    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0
    assert json.loads(d.stdout)["KeyMetadata"]["Enabled"] is False
    plaintext = base64.b64encode(b"nope").decode()
    e = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert e.returncode != 0
    assert "DisabledException" in (e.stderr + e.stdout)
