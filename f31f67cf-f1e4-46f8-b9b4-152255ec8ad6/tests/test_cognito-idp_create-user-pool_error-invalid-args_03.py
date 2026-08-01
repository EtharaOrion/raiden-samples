def test_create_user_pool_rejects_unknown_flag_without_creating_pool(cli, cognito, tmp_path):
    suffix = tmp_path.name.replace("[", "_").replace("]", "_")
    marker_name = f"marker-{suffix}"
    target_name = f"invalid-args-{suffix}"

    marker = cognito.rpc("CreateUserPool", {"PoolName": marker_name})["UserPool"]
    marker_id = marker["Id"]

    before = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert any(pool["Id"] == marker_id and pool["Name"] == marker_name for pool in before)
    assert all(pool["Name"] != target_name for pool in before)

    result = cli(
        "cognito-idp",
        "create-user-pool",
        "--pool-name",
        target_name,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert any(pool["Id"] == marker_id and pool["Name"] == marker_name for pool in after)
    assert all(pool["Name"] != target_name for pool in after)

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": marker_id})["UserPool"]
    assert described["Name"] == marker_name