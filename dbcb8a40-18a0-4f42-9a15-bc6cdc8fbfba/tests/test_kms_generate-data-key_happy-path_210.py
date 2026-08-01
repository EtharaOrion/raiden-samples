import json
import base64


def test_generate_data_key_happy_path(cli, kms, tmp_path):
    # Seed prerequisite state: a symmetric encryption KMS key
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

    # Plaintext should be a valid base64 blob of the requested length
    plaintext_bytes = base64.b64decode(out["Plaintext"])
    assert len(plaintext_bytes) == 32

    # Verify the returned encrypted data key can be decrypted back to the
    # same plaintext through an independent KMS read.
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert decrypt["Plaintext"] == out["Plaintext"]
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id