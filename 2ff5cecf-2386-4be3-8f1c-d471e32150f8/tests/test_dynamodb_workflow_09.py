from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_success(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf10Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf10Tbl", Item={"pk": {"S": "a"}, "v": {"N": "1"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf10Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :new",
        "--condition-expression", "v = :cond",
        "--expression-attribute-values", '{":new":{"N":"42"},":cond":{"N":"1"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf10Tbl", Key={"pk": {"S": "a"}})
    assert from_item(resp["Item"])["v"] == 42
