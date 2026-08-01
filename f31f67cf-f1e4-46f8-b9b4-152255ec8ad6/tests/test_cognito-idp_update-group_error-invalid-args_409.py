def test_update_group_rejects_unknown_attribute_definitions(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "update-group-invalid-args-pool"})["UserPool"]
    pool_id = pool["Id"]
    group_name = "update-group-invalid-args-group"
    original_description = "original description"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": original_description,
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == original_description