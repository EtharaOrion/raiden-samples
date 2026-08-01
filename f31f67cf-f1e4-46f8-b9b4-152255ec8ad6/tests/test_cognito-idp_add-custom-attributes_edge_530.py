def test_add_custom_attributes_adds_attribute_to_pool_schema(cli, cognito, tmp_path):
    pool_name = f"custom-attributes-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert not any(
        attribute.get("Name") == "custom:x"
        for attribute in before["UserPool"].get("SchemaAttributes", [])
    )

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        "Name=x,AttributeDataType=String",
    )
    assert result.returncode == 0

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    matching_attributes = [
        attribute
        for attribute in after["UserPool"].get("SchemaAttributes", [])
        if attribute.get("Name") == "custom:x"
    ]
    assert len(matching_attributes) == 1
    assert matching_attributes[0]["AttributeDataType"] == "String"