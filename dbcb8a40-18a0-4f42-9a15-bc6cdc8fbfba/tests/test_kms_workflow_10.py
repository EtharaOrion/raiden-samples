import json


import json
import base64


def test_workflow_decrypt_missing_key_fails(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "for-badblob")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0
    bad = base64.b64encode(b"not-a-real-ciphertext-blob").decode()
    dec = cli("kms", "decrypt", "--ciphertext-blob", bad)
    assert dec.returncode != 0
    assert "Exception" in (dec.stderr + dec.stdout) or "Invalid" in (dec.stderr + dec.stdout)
