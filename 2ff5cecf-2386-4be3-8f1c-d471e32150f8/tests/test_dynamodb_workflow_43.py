from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_exists_success(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf44Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf44Tbl", Item={"pk": {"S": "a"}, "x": {"S": "1"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf44Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET y = :v",
        "--condition-expression", "attribute_exists(x)",
        "--expression-attribute-values", '{":v":{"S":"2"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf44Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["y"] == "2"
