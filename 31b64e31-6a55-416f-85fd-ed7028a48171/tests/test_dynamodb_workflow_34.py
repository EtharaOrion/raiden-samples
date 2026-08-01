from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_conditional_overwrite_via_ddbclient_check(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf35Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf35Tbl",
                 "--item", '{"pk":{"S":"k"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf35Tbl",
                 "--item", '{"pk":{"S":"k"},"v":{"N":"99"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf35Tbl", Key={"pk": {"S": "k"}})
    assert resp["Item"]["v"]["N"] == "99"
