import json
import base64


def test_generate_data_key_number_of_bytes(cli, kms):
    # Seed a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"Description": "gdk-test", "KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run the command under test
    result = cli("kms", "generate-data-key", "--key-id", key_id, "--number-of-bytes", "1")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert "KeyId" in out

    # Plaintext should decode to exactly 1 byte
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 1

    # The returned KeyId must resolve to the seeded key
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # Independent verification: the ciphertext data key decrypts back to the plaintext
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert decrypt["Plaintext"] == out["Plaintext"]
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id