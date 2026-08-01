def test_generate_random_rejects_empty_custom_key_store_id(cli, kms):
    before = kms.rpc("ListKeys", {})
    before_keys = {
        (key["KeyId"], key["KeyArn"])
        for key in before["Keys"]
    }

    result = cli(
        "kms",
        "generate-random",
        "--custom-key-store-id",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    after = kms.rpc("ListKeys", {})
    after_keys = {
        (key["KeyId"], key["KeyArn"])
        for key in after["Keys"]
    }
    assert after_keys == before_keys