import base64
import json


def test_generate_data_key_happy_path(cli, kms, tmp_path):
    # Seed a symmetric encryption key
    created = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    # Run the command under test
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

    # Plaintext should decode to the requested number of bytes
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # Independently verify: the returned CiphertextBlob decrypts back to the
    # same plaintext data key via the KMS backend.
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext

    # The decrypt resolves to the same underlying key we generated the data key with
    desc = kms.rpc("DescribeKey", {"KeyId": decrypted["KeyId"]})
    assert desc["KeyMetadata"]["KeyId"] == key_id