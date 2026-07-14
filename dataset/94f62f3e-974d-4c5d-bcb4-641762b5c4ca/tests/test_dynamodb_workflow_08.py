from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_word_fails_no_mutation(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf_Reserved1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf_Reserved1", Item={"pk": {"S": "r1"}, "Status": {"S": "orig"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "Wf_Reserved1",
        "--key", '{"pk":{"S":"r1"}}',
        "--update-expression", "SET Status = :v",
        "--expression-attribute-values", '{":v":{"S":"changed"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf_Reserved1", Key={"pk": {"S": "r1"}})
    assert from_item(resp["Item"])["Status"] == "orig"
