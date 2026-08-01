import json
import base64


def test_generate_data_key_happy_path(cli, kms):
    # Seed a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run generate-data-key under test
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

    # Plaintext must be 32 bytes as requested
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # Verify the CiphertextBlob decrypts back to the same plaintext via the backend
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id