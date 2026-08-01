import json
import base64


def test_generate_data_key_one_byte_roundtrip(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "dk-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--number-of-bytes", "1",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id
    plaintext_b64 = out["Plaintext"]
    ciphertext_b64 = out["CiphertextBlob"]

    # plaintext data key should be exactly 1 byte
    assert len(base64.b64decode(plaintext_b64)) == 1

    # Independent read: decrypt the returned ciphertext blob and verify it
    # yields the same plaintext data key.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert dec["Plaintext"] == plaintext_b64
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id