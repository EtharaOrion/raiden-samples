import json


import json
import base64


def test_workflow_disabled_key_encrypt_fails(cli, kms, tmp_path):
    r = cli("kms", "create-key")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    kms.rpc("DisableKey", {"KeyId": key_id})
    plaintext = base64.b64encode(b"nope").decode()
    enc = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert enc.returncode != 0
    assert "Disabled" in enc.stderr
