def test_add_custom_attributes_nonexistent_user_pool(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "add-custom-attributes-nonexistent-control"},
    )
    control_pool_id = created["UserPool"]["Id"]

    before = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": control_pool_id},
    )["UserPool"]
    before_schema = before.get("SchemaAttributes", [])

    region_prefix = control_pool_id.split("_", 1)[0]
    nonexistent_pool_id = f"{region_prefix}_DefinitelyMissingPool123456"

    result = cli(
        "cognito-idp",
        "add-custom-attributes",
        "--user-pool-id",
        nonexistent_pool_id,
        "--custom-attributes",
        '[{"Name":"should_not_exist","AttributeDataType":"String","Mutable":true}]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    after = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": control_pool_id},
    )["UserPool"]
    assert after["Id"] == control_pool_id
    assert after["Name"] == "add-custom-attributes-nonexistent-control"
    assert after.get("SchemaAttributes", []) == before_schema
    assert all(
        attribute.get("Name") != "custom:should_not_exist"
        for attribute in after.get("SchemaAttributes", [])
    )