from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_list_attr(cli, ddb_client, tmp_path):
    t = "wf_list_25"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "l": {"L": [{"S": "x"}, {"N": "3"}]}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"a"}}')
    assert r1.returncode == 0
    items = json.loads(r1.stdout)["Items"]
    assert items[0]["l"]["L"][0]["S"] == "x"
    assert items[0]["l"]["L"][1]["N"] == "3"
    stored = ddb_client.get_item(TableName=t, Key={"pk": {"S": "a"}})["Item"]
    assert stored["l"]["L"][1]["N"] == "3"
