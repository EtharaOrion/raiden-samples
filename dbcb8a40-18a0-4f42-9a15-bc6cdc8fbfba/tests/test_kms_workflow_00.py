import json


import json
import base64


def test_workflow_create_encrypt_decrypt(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "roundtrip")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    plaintext = base64.b64encode(b"hello world").decode()
    e = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert e.returncode == 0
    blob = json.loads(e.stdout)["CiphertextBlob"]
    d = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert d.returncode == 0
    out = json.loads(d.stdout)
    assert out["Plaintext"] == plaintext
