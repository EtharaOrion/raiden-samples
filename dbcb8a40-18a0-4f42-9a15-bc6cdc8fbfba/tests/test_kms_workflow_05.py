import json


import json
import base64


def test_workflow_alias_encrypt_decrypt(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "alias-encrypt")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    aname = "alias/ae-" + key_id[:8]
    ca = cli("kms", "create-alias", "--alias-name", aname, "--target-key-id", key_id)
    assert ca.returncode == 0
    plaintext = base64.b64encode(b"via-alias").decode()
    e = cli("kms", "encrypt", "--key-id", aname, "--plaintext", plaintext)
    assert e.returncode == 0
    blob = json.loads(e.stdout)["CiphertextBlob"]
    d = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert d.returncode == 0
    assert json.loads(d.stdout)["Plaintext"] == plaintext
