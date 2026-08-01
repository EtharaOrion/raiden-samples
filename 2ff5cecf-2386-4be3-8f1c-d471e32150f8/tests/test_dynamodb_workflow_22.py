from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_after_condition_fail_unchanged(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf23Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf23Tbl", Item={"pk": {"S": "a"}, "s": {"S": "keep"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf23Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET s = :new",
        "--condition-expression", "attribute_not_exists(s)",
        "--expression-attribute-values", '{":new":{"S":"changed"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    item = from_item(ddb_client.get_item(TableName="Wf23Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["s"] == "keep"
