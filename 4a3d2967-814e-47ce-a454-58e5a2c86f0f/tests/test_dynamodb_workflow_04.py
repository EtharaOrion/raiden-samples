from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_nonkey_attribute_fails(cli, ddb_client, tmp_path):
    t = "wf_query_nonkey_5"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "color": {"S": "red"}})
    result = cli("dynamodb", "query", "--table-name", t,
                 "--key-condition-expression", "color = :v",
                 "--expression-attribute-values", '{":v":{"S":"red"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
