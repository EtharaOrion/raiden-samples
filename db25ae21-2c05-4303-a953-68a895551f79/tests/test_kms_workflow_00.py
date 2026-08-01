import json


import json
import base64


def test_workflow_create_encrypt_decrypt(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "roundtrip")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    plaintext = base64.b64encode(b"secret-data").decode()
    enc = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert enc.returncode == 0
    blob = json.loads(enc.stdout)["CiphertextBlob"]
    dec = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert dec.returncode == 0
    assert json.loads(dec.stdout)["Plaintext"] == plaintext
