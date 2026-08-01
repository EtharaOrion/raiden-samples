from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multiple_distinct_keys(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfMd1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfMd1",
                 "--item", '{"pk":{"S":"alpha"},"grp":{"S":"g1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfMd1",
                 "--item", '{"pk":{"S":"beta"},"grp":{"S":"g2"}}')
    assert result.returncode == 0
    r1 = ddb_client.get_item(TableName="WfMd1", Key={"pk": {"S": "alpha"}})
    r2 = ddb_client.get_item(TableName="WfMd1", Key={"pk": {"S": "beta"}})
    assert from_item(r1["Item"])["grp"] == "g1"
    assert from_item(r2["Item"])["grp"] == "g2"
