import json
import base64


def test_generate_data_key_happy_path(cli, kms, tmp_path):
    # Seed prerequisite state: create a symmetric encryption KMS key
    created = kms.rpc("CreateKey", {"Description": "gdk-happy-path"})
    key_id = created["KeyMetadata"]["KeyId"]

    # Run the command under test
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert "KeyId" in out

    # Plaintext data key for AES_256 must be 32 bytes
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # The returned KeyId should resolve to the key we created
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # Verify the encrypted data key can be decrypted back to the plaintext
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"].endswith(key_id) or decrypted["KeyId"] == key_id