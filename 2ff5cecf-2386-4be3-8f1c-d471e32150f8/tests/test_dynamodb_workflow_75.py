from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_set_if_not_exists(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf76Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf76Tbl", Item={"pk": {"S": "a"}, "v": {"S": "keep"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf76Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = if_not_exists(v, :v)",
        "--expression-attribute-values", '{":v":{"S":"other"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf76Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["v"] == "keep"
