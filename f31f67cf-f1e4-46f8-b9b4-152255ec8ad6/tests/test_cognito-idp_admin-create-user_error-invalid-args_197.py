def test_admin_create_user_rejects_duplicate_user_pool_id(cli, cognito):
    first_pool = cognito.rpc("CreateUserPool", {
        "PoolName": "duplicate-argument-first-pool",
    })["UserPool"]
    second_pool = cognito.rpc("CreateUserPool", {
        "PoolName": "duplicate-argument-second-pool",
    })["UserPool"]

    result = cli(
        "cognito-idp",
        "admin-create-user",
        "--user-pool-id",
        first_pool["Id"],
        "--username",
        "duplicate-argument-user",
        "--user-pool-id",
        second_pool["Id"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "InvalidParameterException" in result.stderr
        or "DuplicateParameter" in result.stderr
        or "argument --user-pool-id" in result.stderr
    )

    first_users = cognito.rpc("ListUsers", {
        "UserPoolId": first_pool["Id"],
    })["Users"]
    second_users = cognito.rpc("ListUsers", {
        "UserPoolId": second_pool["Id"],
    })["Users"]

    assert all(user["Username"] != "duplicate-argument-user" for user in first_users)
    assert all(user["Username"] != "duplicate-argument-user" for user in second_users)