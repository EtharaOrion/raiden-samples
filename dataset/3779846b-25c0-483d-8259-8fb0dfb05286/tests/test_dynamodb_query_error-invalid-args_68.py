from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_expression(cli, ddb_client):
    ddb_client.create_table(
        TableName="Tbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="Tbl1",
        Item={"pk": {"S": "abc"}, "n": {"N": "5"}},
    )
    result = cli(
        "dynamodb", "query",
        "--table-name", "Tbl1",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"abc"},"extra":{"S":"nope"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr