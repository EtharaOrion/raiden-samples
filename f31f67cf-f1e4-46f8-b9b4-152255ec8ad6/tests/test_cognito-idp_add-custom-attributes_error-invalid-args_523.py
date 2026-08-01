def test_add_custom_attributes_requires_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "add-custom-attributes-missing-pool-id"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    before_schema = before.get("SchemaAttributes", [])
    assert all(
        attribute.get("Name") != "custom:omitted_pool_attr"
        for attribute in before_schema
    )

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--custom-attributes",
        '[{"Name":"omitted_pool_attr","AttributeDataType":"String"}]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert after["Id"] == pool_id
    assert after["Name"] == "add-custom-attributes-missing-pool-id"
    assert all(
        attribute.get("Name") != "custom:omitted_pool_attr"
        for attribute in after.get("SchemaAttributes", [])
    )