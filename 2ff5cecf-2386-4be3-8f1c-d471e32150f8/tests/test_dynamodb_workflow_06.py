from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_absent_key_no_item(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf7Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "get-item", "--table-name", "Wf7Tbl",
        "--key", '{"pk":{"S":"nope"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf7Tbl", Key={"pk": {"S": "nope"}})
    assert "Item" not in resp
