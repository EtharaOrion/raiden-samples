def test_add_custom_attributes_requires_custom_attributes(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "add-custom-attributes-missing-argument"},
    )
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    before_schema = before.get("SchemaAttributes", [])

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--custom-attributes" in result.stderr

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert after["Id"] == pool_id
    assert after["Name"] == "add-custom-attributes-missing-argument"
    assert after.get("SchemaAttributes", []) == before_schema