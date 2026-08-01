from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_after_ddb_update(cli, ddb_client, tmp_path):
    t = "wf_afterupdate_36"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "v": {"S": "old"}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"a"}}')
    assert r1.returncode == 0
    assert json.loads(r1.stdout)["Items"][0]["v"]["S"] == "old"
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "v": {"S": "new"}})
    r2 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"a"}}')
    assert r2.returncode == 0
    assert json.loads(r2.stdout)["Items"][0]["v"]["S"] == "new"
