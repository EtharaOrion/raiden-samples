def test_add_custom_attributes_rejects_unknown_flag_without_mutation(cli, cognito):
    pool_name = "invalid-flag-custom-attributes-pool"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    before_schema_names = {
        attribute["Name"] for attribute in before.get("SchemaAttributes", [])
    }
    assert "custom:department" not in before_schema_names

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        pool_id,
        "--custom-attributes",
        '[{"Name":"department","AttributeDataType":"String","Mutable":true}]',
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    after_schema_names = {
        attribute["Name"] for attribute in after.get("SchemaAttributes", [])
    }
    assert after["Name"] == pool_name
    assert after_schema_names == before_schema_names
    assert "custom:department" not in after_schema_names