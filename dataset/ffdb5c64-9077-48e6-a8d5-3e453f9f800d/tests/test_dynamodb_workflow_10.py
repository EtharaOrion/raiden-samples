from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_attribute_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblQueryBad",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblQueryBad",
                 "--item", '{"pk":{"S":"p1"},"other":{"S":"o1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", "WfTblQueryBad",
                 "--key-condition-expression", "other = :v",
                 "--expression-attribute-values", '{":v":{"S":"o1"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
