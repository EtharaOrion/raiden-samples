import json


import json
import base64


def test_workflow_encrypt_missing_alias_fails(cli, kms, tmp_path):
    r = cli("kms", "create-key")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0
    plaintext = base64.b64encode(b"data").decode()
    enc = cli("kms", "encrypt", "--key-id", "alias/does-not-exist-xyz", "--plaintext", plaintext)
    assert enc.returncode != 0
    assert "NotFound" in enc.stderr
