from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_condition_update_correct_value(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf56Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf56Table",
                 "--item", '{"pk":{"S":"cv1"},"ver":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf56Table",
                 "--key", '{"pk":{"S":"cv1"}}',
                 "--update-expression", "SET ver = :new",
                 "--condition-expression", "ver = :cur",
                 "--expression-attribute-values", '{":new":{"N":"2"},":cur":{"N":"1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf56Table", Key={"pk": {"S": "cv1"}})
    assert from_item(resp["Item"])["ver"] == 2
