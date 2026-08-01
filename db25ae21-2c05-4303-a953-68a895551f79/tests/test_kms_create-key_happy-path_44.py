import json
import base64

def test_create_key_happy_path(cli, kms, tmp_path):
    description = "happy-path-key-under-test"
    result = cli(
        "kms", "create-key",
        "--description", description,
        "--key-usage", "ENCRYPT_DECRYPT",
        "--key-spec", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    meta = out["KeyMetadata"]
    key_id = meta["KeyId"]
    assert key_id

    # Independent read-back via kms
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    dmeta = described["KeyMetadata"]
    assert dmeta["KeyId"] == key_id
    assert dmeta["Description"] == description
    assert dmeta["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert dmeta["Enabled"] is True
    assert dmeta["KeyState"] == "Enabled"

    # Verify functional via encrypt->decrypt round trip
    plaintext = b"round-trip-secret"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext