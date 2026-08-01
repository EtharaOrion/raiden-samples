def test_delete_group_rejects_unknown_attribute_definitions(cli, cognito, tmp_path):
    suffix = tmp_path.name.replace("-", "")
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"delete-group-invalid-{suffix}"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = f"group-{suffix}"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "must remain after invalid CLI invocation",
        },
    )

    result = cli(
        "cognito-idp",
        "delete-group",
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
    assert group["Description"] == "must remain after invalid CLI invocation"