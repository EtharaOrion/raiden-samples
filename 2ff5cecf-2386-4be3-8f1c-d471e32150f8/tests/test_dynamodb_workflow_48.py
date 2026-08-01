from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_negative_number(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf49Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf49Tbl", Item={"pk": {"S": "a"}, "n": {"N": "5"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf49Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "ADD n :d",
        "--expression-attribute-values", '{":d":{"N":"-3"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf49Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["n"] == 2
