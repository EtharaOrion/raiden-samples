def test_add_custom_attributes_happy_path(cli, cognito, tmp_path):
    import json

    pool_name = "custom-attributes-" + "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[:80]
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    attribute_name = "loyaltyTier"
    qualified_name = f"custom:{attribute_name}"

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert qualified_name not in {
        attribute["Name"]
        for attribute in before["UserPool"].get("SchemaAttributes", [])
    }

    custom_attributes = [
        {
            "Name": attribute_name,
            "AttributeDataType": "String",
            "Mutable": True,
            "StringAttributeConstraints": {
                "MinLength": "1",
                "MaxLength": "32",
            },
        }
    ]
    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        json.dumps(custom_attributes),
    )

    assert result.returncode == 0

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    added_attribute = next(
        attribute
        for attribute in after["UserPool"]["SchemaAttributes"]
        if attribute["Name"] == qualified_name
    )
    assert added_attribute["AttributeDataType"] == "String"
    assert added_attribute["Mutable"] is True
    assert added_attribute["StringAttributeConstraints"] == {
        "MinLength": "1",
        "MaxLength": "32",
    }