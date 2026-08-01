from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_chained_updates_accumulate(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf39Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf39Table",
                 "--item", '{"pk":{"S":"acc"},"n":{"N":"0"}}')
    assert result.returncode == 0
    for _ in range(3):
        result = cli("dynamodb", "update-item", "--table-name", "Wf39Table",
                     "--key", '{"pk":{"S":"acc"}}',
                     "--update-expression", "SET n = n + :one",
                     "--expression-attribute-values", '{":one":{"N":"1"}}')
        assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf39Table", Key={"pk": {"S": "acc"}})
    assert from_item(resp["Item"])["n"] == 3
