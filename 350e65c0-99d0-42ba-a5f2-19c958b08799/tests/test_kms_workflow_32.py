import json


import base64
import json
import uuid


def test_workflow_keyusage_encrypt_decrypt(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--key-usage", "ENCRYPT_DECRYPT", "--description", "ed")
    assert r.returncode == 0
    kid = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    pt = base64.b64encode(b"usage").decode()
    e = cli("kms", "encrypt", "--key-id", kid, "--plaintext", pt)
    assert e.returncode == 0
    d = cli("kms", "decrypt", "--ciphertext-blob", json.loads(e.stdout)["CiphertextBlob"])
    assert d.returncode == 0
    assert json.loads(d.stdout)["Plaintext"] == pt
