from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_overwrite_existing(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf21Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf21Tbl", Item={"pk": {"S": "a"}, "v": {"S": "old"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf21Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"fresh"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf21Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["v"] == "fresh"
