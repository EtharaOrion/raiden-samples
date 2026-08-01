import json


import json
import base64


def test_workflow_generate_data_key_decrypt(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "gdk")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    g = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert g.returncode == 0
    gout = json.loads(g.stdout)
    plaintext = gout["Plaintext"]
    blob = gout["CiphertextBlob"]
    d = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert d.returncode == 0
    assert json.loads(d.stdout)["Plaintext"] == plaintext
