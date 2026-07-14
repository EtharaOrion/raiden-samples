from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_word_fails(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfRsv1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfRsv1", Item={"pk": {"S": "k"}, "Status": {"S": "old"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WfRsv1",
        "--key", '{"pk":{"S":"k"}}',
        "--update-expression", "SET Status = :v",
        "--expression-attribute-values", '{":v":{"S":"new"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="WfRsv1", Key={"pk": {"S": "k"}})
    assert resp["Item"]["Status"]["S"] == "old"
