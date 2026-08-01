from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_three_and_verify_each(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf21Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for i in range(3):
        result = cli("dynamodb", "put-item", "--table-name", "Wf21Table",
                     "--item", '{"pk":{"S":"k%d"},"n":{"N":"%d"}}' % (i, i))
        assert result.returncode == 0
    for i in range(3):
        resp = ddb_client.get_item(TableName="Wf21Table", Key={"pk": {"S": "k%d" % i}})
        assert from_item(resp["Item"])["n"] == i
