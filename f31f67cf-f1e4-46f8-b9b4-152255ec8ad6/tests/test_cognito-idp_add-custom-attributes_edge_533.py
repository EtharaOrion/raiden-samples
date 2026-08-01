def test_add_custom_attributes_adds_attribute_to_pool_schema(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "add-custom-attributes-edge-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    attribute_name = "xxxxxxxxxxxxxxxxxxxxxxxxx"

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert all(
        attribute.get("Name") != f"custom:{attribute_name}"
        for attribute in before.get("SchemaAttributes", [])
    )

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        f"Name={attribute_name},AttributeDataType=String",
    )
    assert result.returncode == 0

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    custom_attribute = next(
        attribute
        for attribute in after.get("SchemaAttributes", [])
        if attribute.get("Name") == f"custom:{attribute_name}"
    )
    assert custom_attribute["AttributeDataType"] == "String"