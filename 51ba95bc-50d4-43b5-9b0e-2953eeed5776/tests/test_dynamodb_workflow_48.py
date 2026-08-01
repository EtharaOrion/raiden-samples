from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_provisioned_throughput_create(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_prov1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--provisioned-throughput", '{"ReadCapacityUnits":5,"WriteCapacityUnits":5}')
    assert result.returncode == 0
    assert "Tbl_prov1" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_prov1",
                 "--item", '{"pk":{"S":"pv1"},"v":{"S":"ok"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_prov1", Key={"pk": {"S": "pv1"}})
    assert from_item(resp["Item"]) == {"pk": "pv1", "v": "ok"}
