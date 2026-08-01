def test_add_custom_attributes_invalid_args(cli, cognito, tmp_path):
    pool_name = f"invalid-custom-attributes-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        "{",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid JSON" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == pool_name
    assert all(
        attribute.get("Name") != "custom:should_not_exist"
        for attribute in described["UserPool"].get("SchemaAttributes", [])
    )