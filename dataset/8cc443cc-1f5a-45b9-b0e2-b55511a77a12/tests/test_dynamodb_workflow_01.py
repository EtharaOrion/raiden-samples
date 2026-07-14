from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_update_get_mutation(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfMutTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )

    result = cli("dynamodb", "put-item", "--table-name", "WfMutTbl",
                 "--item", '{"pk":{"S":"m1"},"status":{"S":"old"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "update-item", "--table-name", "WfMutTbl",
                 "--key", '{"pk":{"S":"m1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="WfMutTbl", Key={"pk": {"S": "m1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["status"] == "new"
