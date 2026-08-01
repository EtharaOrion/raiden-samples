from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_existing_item(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf19Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf19Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #d = :v",
        "--expression-attribute-names", '{"#d":"data"}',
        "--expression-attribute-values", '{":v":{"S":"hello"}}',
    )
    assert result.returncode == 0
    result2 = cli(
        "dynamodb", "get-item", "--table-name", "Wf19Tbl",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert result2.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf19Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["data"] == "hello"
