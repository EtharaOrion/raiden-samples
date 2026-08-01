def test_describe_user_pool_nonexistent_error(cli, cognito):
    result = cli(
        "cognito-idp",
        "describe-user-pool",
        "--user-pool-id",
        "local_doesnotexist123",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "NotAuthorized" in result.stderr

    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    ids = [p["Id"] for p in listed.get("UserPools", [])]
    assert "local_doesnotexist123" not in ids