import json
import base64


def test_generate_data_key_aes_128(cli, kms):
    # Seed: create a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"Description": "dk-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run the command under test
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_128",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert "KeyId" in out

    # AES_128 -> 16 bytes plaintext
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 16

    # Verify the returned KeyId refers to the same seeded key
    desc = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert desc["KeyMetadata"]["KeyId"] == key_id

    # Verify the CiphertextBlob decrypts back to the plaintext (round trip)
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id