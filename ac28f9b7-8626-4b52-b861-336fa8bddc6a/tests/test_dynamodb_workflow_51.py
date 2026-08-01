from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_bool_attribute(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf52Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf52Table",
                 "--item", '{"pk":{"S":"ub1"},"active":{"BOOL":false}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf52Table",
                 "--key", '{"pk":{"S":"ub1"}}',
                 "--update-expression", "SET active = :a",
                 "--expression-attribute-values", '{":a":{"BOOL":true}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf52Table", Key={"pk": {"S": "ub1"}})
    assert from_item(resp["Item"])["active"] is True
