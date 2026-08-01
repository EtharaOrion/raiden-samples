import json
import base64


def test_generate_data_key_happy_path(cli, kms, tmp_path):
    # Seed a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"Description": "gdk-test", "KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Generate a data key with an explicit spec
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Plaintext key must be 32 bytes for AES_256
    plaintext_bytes = base64.b64decode(out["Plaintext"])
    assert len(plaintext_bytes) == 32

    # Independent read: the encrypted data key must decrypt back to the same plaintext
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext_bytes
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id

    # And the seeded key still describes fine and is enabled
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["Enabled"] is True