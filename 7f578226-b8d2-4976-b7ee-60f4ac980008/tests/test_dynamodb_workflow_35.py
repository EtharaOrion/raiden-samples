from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_three_creates_all_listed(cli, ddb_client, tmp_path):
    names = ["WfTbl33a", "WfTbl33b", "WfTbl33c"]
    for t in names:
        result = cli("dynamodb", "create-table", "--table-name", t,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    listed = set(ddb_client.list_tables()["TableNames"])
    for t in names:
        assert t in listed
