def test_list_user_pools_max_results_edge(cli, cognito, tmp_path):
    import json
    import uuid

    pool_name = f"list-edge-{uuid.uuid4().hex}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "60",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in output["UserPools"]
    )

    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in listed["UserPools"]
    )

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == pool_name