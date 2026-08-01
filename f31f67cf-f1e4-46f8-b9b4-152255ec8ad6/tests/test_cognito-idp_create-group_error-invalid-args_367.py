def test_create_group_rejects_unknown_flag_without_creating_group(cli, cognito):
    pool_name = "create-group-invalid-args-pool"
    group_name = "should-not-be-created"

    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert before.get("Groups", []) == []

    result = cli(
        "cognito-idp",
        "create-group",
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

    after = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert all(group["GroupName"] != group_name for group in after.get("Groups", []))

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == pool_name