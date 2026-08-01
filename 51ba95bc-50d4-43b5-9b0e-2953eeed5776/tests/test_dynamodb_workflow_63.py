from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_via_ddb_get_via_cli(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_sdgc1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_sdgc1",
                 "--item", '{"pk":{"S":"sd1"},"v":{"N":"77"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_sdgc1",
                 "--key", '{"pk":{"S":"sd1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_sdgc1", Key={"pk": {"S": "sd1"}})
    assert from_item(resp["Item"]) == {"pk": "sd1", "v": 77}
