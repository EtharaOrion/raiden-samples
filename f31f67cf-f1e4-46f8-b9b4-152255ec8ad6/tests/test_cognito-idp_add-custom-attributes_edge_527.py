def test_add_custom_attributes_adds_attribute_to_pool_schema(cli, cognito, tmp_path):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"custom-attributes-{tmp_path.name}"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert not any(
        attribute.get("Name") == "custom:edge_code"
        for attribute in before.get("SchemaAttributes", [])
    )

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        '[{"Name":"edge_code","AttributeDataType":"String"}]',
    )
    assert result.returncode == 0

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    matching_attributes = [
        attribute
        for attribute in after.get("SchemaAttributes", [])
        if attribute.get("Name") == "custom:edge_code"
    ]
    assert len(matching_attributes) == 1
    assert matching_attributes[0]["AttributeDataType"] == "String"