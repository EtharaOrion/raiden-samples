import json
import base64

def test_create_key_symmetric_default(cli, kms):
    result = cli("kms", "create-key", "--key-spec", "SYMMETRIC_DEFAULT")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    meta = out["KeyMetadata"]
    key_id = meta["KeyId"]
    assert key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    dmeta = described["KeyMetadata"]
    assert dmeta["KeyId"] == key_id
    assert dmeta["KeySpec"] == "SYMMETRIC_DEFAULT"
    assert dmeta["Enabled"] is True
    assert dmeta["KeyState"] == "Enabled"

    plaintext = b"round-trip-secret"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext