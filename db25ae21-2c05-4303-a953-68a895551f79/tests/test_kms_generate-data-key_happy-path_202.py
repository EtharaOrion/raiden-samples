import json
import base64


def test_generate_data_key_happy_path(cli, kms):
    # Seed prerequisite state: create a symmetric encryption key
    create = kms.rpc("CreateKey", {"Description": "gdk-test", "KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run the command under test
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--number-of-bytes", "32",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Plaintext must be the requested length
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # Independent read: the returned encrypted data key must decrypt back
    # to the same plaintext via the backend Decrypt operation.
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id

    # Confirm the key used still exists and is enabled
    describe = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert describe["KeyMetadata"]["KeyId"] == key_id
    assert describe["KeyMetadata"]["Enabled"] is True