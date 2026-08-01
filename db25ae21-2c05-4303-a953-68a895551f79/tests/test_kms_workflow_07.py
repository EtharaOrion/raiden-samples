import json


import json
import base64


def test_workflow_disable_enable_encrypt(cli, kms, tmp_path):
    r = cli("kms", "create-key")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    kms.rpc("DisableKey", {"KeyId": key_id})
    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0
    assert json.loads(d.stdout)["KeyMetadata"]["Enabled"] is False
    e = cli("kms", "enable-key", "--key-id", key_id)
    assert e.returncode == 0
    d2 = cli("kms", "describe-key", "--key-id", key_id)
    assert d2.returncode == 0
    assert json.loads(d2.stdout)["KeyMetadata"]["Enabled"] is True
    plaintext = base64.b64encode(b"after-enable").decode()
    enc = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert enc.returncode == 0
