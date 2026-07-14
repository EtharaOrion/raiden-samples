from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_add_attribute_getitem(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf_UpdAdd1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf_UpdAdd1", Item={"pk": {"S": "k1"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "Wf_UpdAdd1",
        "--key", '{"pk":{"S":"k1"}}',
        "--update-expression", "SET score = :s",
        "--expression-attribute-values", '{":s":{"N":"42"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf_UpdAdd1", Key={"pk": {"S": "k1"}})
    assert from_item(resp["Item"])["score"] == 42
