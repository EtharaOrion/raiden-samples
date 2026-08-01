def test_add_custom_attributes_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"custom-attrs-{uuid.uuid4().hex}"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert all(
        attribute["Name"] != "custom:favorite_color"
        for attribute in before.get("SchemaAttributes", [])
    )

    custom_attributes = [
        {
            "Name": "favorite_color",
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
    added = [
        attribute
        for attribute in after.get("SchemaAttributes", [])
        if attribute["Name"] == "custom:favorite_color"
    ]
    assert len(added) == 1
    assert added[0]["AttributeDataType"] == "String"
    assert added[0]["Mutable"] is True