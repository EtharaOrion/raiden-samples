def test_delete_group_rejects_unknown_flag_without_deleting_group(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-group-invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]
    group_name = "group-must-remain"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Group retained after invalid CLI arguments",
        },
    )

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
        "--not-a-real-flag",
        "x",
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