def test_add_custom_attributes_adds_attribute_to_pool_schema(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "add-custom-attributes-edge"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert all(
        attribute.get("Name") != "custom:edge_attribute"
        for attribute in before.get("SchemaAttributes", [])
    )

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        '[{"Name":"edge_attribute","AttributeDataType":"String"}]',
    )
    assert result.returncode == 0

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    matching_attributes = [
        attribute
        for attribute in after.get("SchemaAttributes", [])
        if attribute.get("Name") == "custom:edge_attribute"
    ]
    assert len(matching_attributes) == 1
    assert matching_attributes[0]["AttributeDataType"] == "String"