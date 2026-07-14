from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_item_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfPMT1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "NoSuchTableWfPMT",
                 "--item", '{"pk":{"S":"a1"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    resp = ddb_client.get_item(TableName="WfPMT1", Key={"pk": {"S": "a1"}})
    assert "Item" not in resp
