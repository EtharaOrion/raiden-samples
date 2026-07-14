from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_word_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfResvTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfResvTbl", Item={"pk": {"S": "a"}, "Status": {"S": "old"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfResvTbl",
                 "--key", '{"pk":{"S":"a"}}',
                 "--update-expression", "SET Status = :v",
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="WfResvTbl", Key={"pk": {"S": "a"}}, ConsistentRead=True)
    assert from_item(resp["Item"])["Status"] == "old"
