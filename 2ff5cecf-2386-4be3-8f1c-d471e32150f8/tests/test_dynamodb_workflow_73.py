from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_verify_get_error(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf74Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf74Tbl", Item={"pk": {"S": "a"}})
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf74Tbl")
    assert rd.returncode == 0
    assert "Wf74Tbl" not in ddb_client.list_tables()["TableNames"]
    rg = cli(
        "dynamodb", "get-item", "--table-name", "Wf74Tbl",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert rg.returncode != 0
    assert "ResourceNotFoundException" in rg.stderr
