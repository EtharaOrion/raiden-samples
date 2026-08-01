from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_after_add_new_key(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf59Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf59Tbl", Item={"pk": {"S": "a"}, "one": {"S": "1"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf59Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET two = :v",
        "--expression-attribute-values", '{":v":{"S":"2"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf59Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["one"] == "1" and item["two"] == "2"
