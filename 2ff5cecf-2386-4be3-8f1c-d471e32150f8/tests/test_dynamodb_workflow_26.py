from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_binary_attr(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf27Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf27Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET flag = :v",
        "--expression-attribute-values", '{":v":{"BOOL":true}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf27Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["flag"] is True
