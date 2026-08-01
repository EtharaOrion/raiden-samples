from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_delete_persistence(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf70Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf70Tbl", Item={"pk": {"S": "a"}, "locked": {"BOOL": True}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf70Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :v",
        "--condition-expression", "locked = :f",
        "--expression-attribute-values", '{":v":{"S":"x"},":f":{"BOOL":false}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    item = from_item(ddb_client.get_item(TableName="Wf70Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert "v" not in item
