from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_get_unchanged(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf39Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf39Tbl", Item={"pk": {"S": "a"}, "keep": {"S": "orig"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf39Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET Status = :v",
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    item = from_item(ddb_client.get_item(TableName="Wf39Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["keep"] == "orig"
