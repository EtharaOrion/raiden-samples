from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_delete_lifecycle(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf_Lifecycle1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf_Lifecycle1", Item={"pk": {"S": "L1"}})
    up = cli(
        "dynamodb", "update-item",
        "--table-name", "Wf_Lifecycle1",
        "--key", '{"pk":{"S":"L1"}}',
        "--update-expression", "SET label = :l",
        "--expression-attribute-values", '{":l":{"S":"tagged"}}',
    )
    assert up.returncode == 0
    resp = ddb_client.get_item(TableName="Wf_Lifecycle1", Key={"pk": {"S": "L1"}})
    assert from_item(resp["Item"])["label"] == "tagged"
    dl = cli(
        "dynamodb", "delete-item",
        "--table-name", "Wf_Lifecycle1",
        "--key", '{"pk":{"S":"L1"}}',
    )
    assert dl.returncode == 0
    resp2 = ddb_client.get_item(TableName="Wf_Lifecycle1", Key={"pk": {"S": "L1"}})
    assert "Item" not in resp2
