import json
import base64


def test_generate_data_key_happy_path(cli, kms, tmp_path):
    # Prerequisite: create a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"Description": "gen-data-key-test"})
    key_id = create["KeyMetadata"]["KeyId"]

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

    # Plaintext AES_256 must be 32 bytes
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # Verify the returned KeyId resolves to our created key via independent read
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # Independent verification: the CiphertextBlob decrypts back to the plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id