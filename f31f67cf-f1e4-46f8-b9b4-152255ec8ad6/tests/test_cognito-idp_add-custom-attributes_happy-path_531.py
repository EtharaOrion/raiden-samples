def test_add_custom_attributes_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"custom-attrs-{uuid.uuid4().hex}"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    custom_attributes = [
        {
            "Name": "department",
            "AttributeDataType": "String",
            "Mutable": True,
            "StringAttributeConstraints": {
                "MinLength": "1",
                "MaxLength": "64",
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

    described_pool = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    schema_by_name = {
        attribute["Name"]: attribute
        for attribute in described_pool["SchemaAttributes"]
    }

    assert "custom:department" in schema_by_name
    added_attribute = schema_by_name["custom:department"]
    assert added_attribute["AttributeDataType"] == "String"
    assert added_attribute["Mutable"] is True
    assert added_attribute["StringAttributeConstraints"] == {
        "MinLength": "1",
        "MaxLength": "64",
    }