from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_item_then_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf3Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf3Tbl", Item={"pk": {"S": "a"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf3Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf3Tbl", Key={"pk": {"S": "a"}})
    assert from_item(resp["Item"])["status"] == "active"
