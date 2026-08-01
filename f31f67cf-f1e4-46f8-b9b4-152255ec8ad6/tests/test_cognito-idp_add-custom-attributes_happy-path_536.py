def test_add_custom_attributes_happy_path(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "add-custom-attributes-happy-path"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    assert all(
        attribute.get("Name") != "custom:employeeCode"
        for attribute in before.get("SchemaAttributes", [])
    )

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        json.dumps(
            [
                {
                    "Name": "employeeCode",
                    "AttributeDataType": "String",
                    "Mutable": True,
                }
            ]
        ),
    )

    assert result.returncode == 0

    after = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    custom_attribute = next(
        attribute
        for attribute in after["SchemaAttributes"]
        if attribute.get("Name") == "custom:employeeCode"
    )
    assert custom_attribute["AttributeDataType"] == "String"
    assert custom_attribute["Mutable"] is True