def test_add_custom_attributes_rejects_empty_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "add-custom-attributes-invalid-id"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    before_schema = before.get("SchemaAttributes", [])
    assert "custom:invalid_attempt_marker" not in {
        attribute["Name"] for attribute in before_schema
    }

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        "",
        "--custom-attributes",
        '[{"Name":"invalid_attempt_marker","AttributeDataType":"String"}]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "Invalid length" in result.stderr
        or "InvalidParameterException" in result.stderr
    )

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert after["Id"] == pool_id
    assert after["Name"] == "add-custom-attributes-invalid-id"
    assert "custom:invalid_attempt_marker" not in {
        attribute["Name"] for attribute in after.get("SchemaAttributes", [])
    }