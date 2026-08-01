import json
import base64


def test_generate_data_key_happy_path(cli, kms, tmp_path):
    # Prerequisite: create a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run generate-data-key under test
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert "KeyId" in out

    # Plaintext must be valid base64 and AES_256 => 32 bytes
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # The returned KeyId must resolve to our key
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # Verify the CiphertextBlob decrypts back to the same plaintext (round trip)
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert decrypt["Plaintext"] == out["Plaintext"]
    assert decrypt["KeyId"].endswith(key_id) or key_id in decrypt["KeyId"]