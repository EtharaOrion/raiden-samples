def test_create_user_pool_rejects_empty_pool_name(cli, cognito):
    before = cognito.rpc("ListUserPools", {"MaxResults": 60})
    before_pools = {
        pool["Id"]: pool["Name"] for pool in before.get("UserPools", [])
    }

    result = cli(
        "cognito-idp",
        "create-user-pool",
        "--pool-name",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    after = cognito.rpc("ListUserPools", {"MaxResults": 60})
    after_pools = {
        pool["Id"]: pool["Name"] for pool in after.get("UserPools", [])
    }
    assert after_pools == before_pools