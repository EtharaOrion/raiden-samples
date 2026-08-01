def test_update_group_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-group-missing-pool-id-test"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "existing-group"
    original_description = "original description"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": original_description,
            "Precedence": 10,
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        group_name,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == original_description
    assert group["Precedence"] == 10