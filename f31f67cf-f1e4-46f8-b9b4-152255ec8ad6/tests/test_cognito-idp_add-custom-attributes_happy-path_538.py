def test_add_custom_attributes_adds_attribute_to_pool_schema(cli, cognito):
    import json
    import uuid

    pool_name = f"custom-attributes-{uuid.uuid4().hex}"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert "custom:loyaltyTier" not in {
        attribute["Name"] for attribute in before.get("SchemaAttributes", [])
    }

    custom_attributes = [
        {
            "Name": "loyaltyTier",
            "AttributeDataType": "String",
            "Mutable": True,
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

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    added_attribute = next(
        (
            attribute
            for attribute in after.get("SchemaAttributes", [])
            if attribute["Name"] == "custom:loyaltyTier"
        ),
        None,
    )
    assert added_attribute is not None
    assert added_attribute["AttributeDataType"] == "String"
    assert added_attribute["Mutable"] is True