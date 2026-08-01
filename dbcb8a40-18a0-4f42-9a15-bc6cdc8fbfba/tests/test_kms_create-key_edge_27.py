import json
import base64


def test_create_key_customer_master_key_spec_symmetric_default(cli, kms, tmp_path):
    result = cli("kms", "create-key", "--customer-master-key-spec", "SYMMETRIC_DEFAULT")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    key_id = out["KeyMetadata"]["KeyId"]
    assert key_id

    # Independent read-back via kms
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    md = desc["KeyMetadata"]
    assert md["KeyId"] == key_id
    assert md["Enabled"] is True
    assert md["KeyState"] == "Enabled"
    assert md.get("KeyUsage", "ENCRYPT_DECRYPT") == "ENCRYPT_DECRYPT"

    # Verify usability with an encrypt->decrypt round trip
    plaintext = b"symmetric-default-roundtrip"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext