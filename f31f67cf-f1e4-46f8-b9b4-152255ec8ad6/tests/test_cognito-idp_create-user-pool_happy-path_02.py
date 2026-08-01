def test_create_user_pool_happy_path(cli, cognito):
    import json

    pool_name = "black-box-create-user-pool"
    result = cli(
        "cognito-idp",
        "create-user-pool",
        "--pool-name",
        pool_name,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    pool_id = output["UserPool"]["Id"]
    assert output["UserPool"]["Name"] == pool_name

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name

    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in listed["UserPools"]
    )