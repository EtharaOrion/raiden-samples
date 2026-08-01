from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_on_missing_item(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf66Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf66Tbl",
        "--key", '{"pk":{"S":"nope"}}',
        "--update-expression", "SET v = :v",
        "--condition-expression", "attribute_exists(pk)",
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf66Tbl", Key={"pk": {"S": "nope"}})
    assert "Item" not in resp
