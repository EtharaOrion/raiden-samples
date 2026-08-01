from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_get_number_removed(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf16Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf16Tbl", Item={"pk": {"S": "a"}, "gone": {"S": "x"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf16Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "REMOVE gone",
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf16Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert "gone" not in item
