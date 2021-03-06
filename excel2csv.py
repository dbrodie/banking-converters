import csv
from lxml import etree


def element_text(elem: etree.Element):
    return ' '.join([t for t in elem.itertext()])


def html_table_to_list(html_path, table_xpath):
    html = etree.parse(html_path, etree.HTMLParser())
    tables = html.getroot().xpath(table_xpath)

    if not tables:
        raise RuntimeError('XPath found nothing (' + table_xpath + ')')

    thead_tr = tables[0].xpath('thead/tr')
    header = []
    if len(thead_tr) > 0:
        for th in thead_tr[0].iterchildren('th'):
            header.append(element_text(th))

    tbody_tr = tables[0].xpath('tbody/tr')
    rows = []
    for tr in tbody_tr:
        row = []
        for td in tr.iterchildren('td'):
            row.append(element_text(td))
        rows.append(row)

    return header, rows


def spreadsheetml_to_list(xml_path, rows_xpath, xml_namespaces):
    xml = etree.parse(xml_path)

    rows = xml.getroot().xpath(rows_xpath, namespaces=xml_namespaces)
    results = []
    for row in rows:
        values = []
        for cell in row.iterchildren('{*}Cell'):
            data = cell.find('{*}Data')
            if data is not None:
                values.append(element_text(data))
        if values:
            results.append(values)

    return results


def list_to_csv(lst, csv_path, drop_columns=None, encoding='utf-8', dialect=csv.unix_dialect):
    assert lst
    drop_cols = drop_columns if drop_columns else []
    with open(csv_path, 'w', encoding=encoding) as f:
        writer = csv.writer(f, dialect=dialect)
        for x in lst:
            curr_row = list(x)
            # This list should contain a table, so ensure all rows have the same size
            assert len(curr_row) == len(lst[0]), "Expected same length, got {} vs. {}".format(lst[0], x)
            for i in sorted(drop_cols, reverse=True):
                curr_row.pop(i)
            writer.writerow(curr_row)
