import json
import base64


def test_create_key_customer_master_key_spec_symmetric(cli, kms):
    result = cli("kms", "create-key", "--customer-master-key-spec", "SYMMETRIC_DEFAULT")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    key_id = out["KeyMetadata"]["KeyId"]
    assert key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    meta = described["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Enabled"] is True
    assert meta["KeyState"] == "Enabled"

    # verify usability via an encrypt/decrypt round trip
    plaintext = b"hello-symmetric-default"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext