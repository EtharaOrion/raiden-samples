from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_tables_isolation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfIsoA",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "WfIsoB",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfIsoA",
                 "--item", '{"pk":{"S":"k"},"src":{"S":"A"}}')
    assert result.returncode == 0
    respa = ddb_client.get_item(TableName="WfIsoA", Key={"pk": {"S": "k"}})
    assert from_item(respa["Item"]) == {"pk": "k", "src": "A"}
    respb = ddb_client.get_item(TableName="WfIsoB", Key={"pk": {"S": "k"}})
    assert "Item" not in respb
