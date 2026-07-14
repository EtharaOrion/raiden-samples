from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_update_get_mutation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf2Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf2Tbl",
                 "--item", '{"pk":{"S":"k1"},"status":{"S":"old"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "update-item", "--table-name", "Wf2Tbl",
                 "--key", '{"pk":{"S":"k1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="Wf2Tbl", Key={"pk": {"S": "k1"}})
    assert "Item" in resp
    from _ddb_http import from_item
    assert from_item(resp["Item"])["status"] == "new"
