import json
import base64


def test_generate_data_key_happy_path(cli, kms, tmp_path):
    # Seed prerequisite: create a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"Description": "gdk-test", "KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run command under test
    result = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert "KeyId" in out

    # Plaintext is base64 of a 256-bit (32-byte) key
    plaintext_bytes = base64.b64decode(out["Plaintext"])
    assert len(plaintext_bytes) == 32

    # The returned KeyId should reference the key we created
    assert key_id in out["KeyId"]

    # Independent read: the CiphertextBlob must decrypt back to the plaintext data key
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext_bytes
    assert key_id in decrypt["KeyId"]