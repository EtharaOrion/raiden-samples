def test_add_custom_attributes_rejects_unknown_attribute_definitions(cli, cognito):
    import json

    pool_name = "add-custom-attributes-invalid-args"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    before_schema = before.get("SchemaAttributes", [])

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        json.dumps(
            [
                {
                    "Name": "rejected_attribute",
                    "AttributeDataType": "String",
                    "Mutable": True,
                }
            ]
        ),
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert after["Name"] == pool_name
    assert after.get("SchemaAttributes", []) == before_schema
    assert all(
        attribute.get("Name") != "custom:rejected_attribute"
        for attribute in after.get("SchemaAttributes", [])
    )