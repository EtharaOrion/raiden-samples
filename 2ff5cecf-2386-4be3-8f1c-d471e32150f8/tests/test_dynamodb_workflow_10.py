from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_then_get_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf11Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf11Tbl", Item={"pk": {"S": "a"}})
    result = cli("dynamodb", "delete-table", "--table-name", "Wf11Tbl")
    assert result.returncode == 0
    result = cli(
        "dynamodb", "get-item", "--table-name", "Wf11Tbl",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
