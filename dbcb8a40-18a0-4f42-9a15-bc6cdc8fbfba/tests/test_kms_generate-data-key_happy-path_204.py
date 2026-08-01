import base64
import json


def test_generate_data_key_happy_path(cli, kms, tmp_path):
    # Seed: create a symmetric encryption KMS key
    created = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    # Run command under test
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Plaintext should be 32 bytes for AES_256
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # Independent read: decrypt the returned CiphertextBlob and confirm it
    # round-trips back to the plaintext data key.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id