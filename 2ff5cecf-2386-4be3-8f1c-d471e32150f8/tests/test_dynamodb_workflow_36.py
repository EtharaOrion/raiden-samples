from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_between_two_gets(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf37Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf37Tbl", Item={"pk": {"S": "a"}})
    r1 = cli(
        "dynamodb", "get-item", "--table-name", "Wf37Tbl",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert r1.returncode == 0
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf37Tbl")
    assert rd.returncode == 0
    r2 = cli(
        "dynamodb", "get-item", "--table-name", "Wf37Tbl",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert r2.returncode != 0
    assert "ResourceNotFoundException" in r2.stderr
