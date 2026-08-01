def test_list_groups_nonexistent_user_pool(cli, cognito):
    pool_name = "list-groups-nonexistent-test"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]
    nonexistent_pool_id = pool_id + "nonexistent"

    result = cli(
        "cognito-idp",
        "list-groups",
        "--user-pool-id",
        nonexistent_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert groups["Groups"] == []