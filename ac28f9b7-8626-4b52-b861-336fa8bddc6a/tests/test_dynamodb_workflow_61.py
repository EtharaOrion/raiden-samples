from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_names_alias(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf62Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf62Table",
                 "--item", '{"pk":{"S":"cn1"},"Status":{"S":"live"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf62Table",
                 "--item", '{"pk":{"S":"cn1"},"Status":{"S":"dead"}}',
                 "--condition-expression", "#s = :v",
                 "--expression-attribute-names", '{"#s":"Status"}',
                 "--expression-attribute-values", '{":v":{"S":"live"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf62Table", Key={"pk": {"S": "cn1"}})
    assert from_item(resp["Item"])["Status"] == "dead"
