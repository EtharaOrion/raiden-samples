from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_wrong_type_value(cli, ddb_client, tmp_path):
    t = "wf_wrongtype_34"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "N"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"id": {"N": "1"}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "id = :v",
             "--expression-attribute-values", '{":v":{"S":"notanumber"}}')
    assert r1.returncode != 0
    assert "ValidationException" in r1.stderr
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["id"]["N"] for i in json.loads(r2.stdout)["Items"]} == {"1"}
