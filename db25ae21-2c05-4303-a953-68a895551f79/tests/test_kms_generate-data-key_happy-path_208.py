import json
import base64


def test_generate_data_key_happy_path(cli, kms):
    # Seed a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Generate a data key under the seeded key
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--number-of-bytes", "32",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert "KeyId" in out

    # Plaintext should be the requested length
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # The returned KeyId must resolve to the seeded key
    desc = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert desc["KeyMetadata"]["KeyId"] == key_id

    # The encrypted data key must decrypt back to the plaintext (round trip)
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext