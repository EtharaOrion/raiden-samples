from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_and_readback(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf35Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf35Tbl", Item={"pk": {"S": "a"}, "n": {"N": "0"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf35Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET n = :new",
        "--condition-expression", "n = :old",
        "--expression-attribute-values", '{":new":{"N":"1"},":old":{"N":"0"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf35Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["n"] == 1
