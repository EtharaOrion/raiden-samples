import json


import json
import base64


def test_workflow_alias_encrypt_roundtrip(cli, kms, tmp_path):
    r = cli("kms", "create-key")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    alias = "alias/enc-alias-%s" % key_id[:8]
    a = cli("kms", "create-alias", "--alias-name", alias, "--target-key-id", key_id)
    assert a.returncode == 0
    la = cli("kms", "list-aliases")
    assert la.returncode == 0
    names = [x["AliasName"] for x in json.loads(la.stdout)["Aliases"]]
    assert alias in names
    plaintext = base64.b64encode(b"via-alias").decode()
    enc = cli("kms", "encrypt", "--key-id", alias, "--plaintext", plaintext)
    assert enc.returncode == 0
    blob = json.loads(enc.stdout)["CiphertextBlob"]
    dec = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert dec.returncode == 0
    assert json.loads(dec.stdout)["Plaintext"] == plaintext
