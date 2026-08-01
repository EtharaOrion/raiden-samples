def test_add_custom_attributes_happy_path(cli, cognito):
    import json
    import uuid

    attribute_name = "project_code"
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"custom-attributes-{uuid.uuid4().hex}"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert attribute_name not in {
        attribute["Name"] for attribute in before.get("SchemaAttributes", [])
    }
    assert f"custom:{attribute_name}" not in {
        attribute["Name"] for attribute in before.get("SchemaAttributes", [])
    }

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        json.dumps(
            [
                {
                    "Name": attribute_name,
                    "AttributeDataType": "String",
                    "Mutable": True,
                }
            ]
        ),
    )

    assert result.returncode == 0

    described = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    attributes = {
        attribute["Name"]: attribute
        for attribute in described.get("SchemaAttributes", [])
    }
    custom_attribute = attributes[f"custom:{attribute_name}"]
    assert custom_attribute["AttributeDataType"] == "String"
    assert custom_attribute["Mutable"] is True