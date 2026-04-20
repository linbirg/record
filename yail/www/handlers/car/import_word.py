import io
from typing import List, Dict, Tuple
from docx import Document


def parse_word_table(file_bytes: bytes) -> Tuple[List[Dict], List[Dict]]:
    """
    解析 Word 文档中的表格，提取姓名和车牌号

    Args:
        file_bytes: Word 文件字节数据

    Returns:
        (valid_rows, error_rows)
        valid_rows: [{'name': str, 'carNo': str}, ...]
        error_rows: [{'row': int, 'message': str}, ...]
    """
    doc = Document(io.BytesIO(file_bytes))

    if not doc.tables:
        raise ValueError("文档中没有找到表格")

    table = doc.tables[0]
    if len(table.rows) < 2:
        raise ValueError("文档中没有找到车辆数据")

    header_row = table.rows[0]
    name_col = -1
    carNo_col = -1

    for i, cell in enumerate(header_row.cells):
        text = cell.text.strip()
        if '姓名' in text:
            name_col = i
        elif '车牌号' in text:
            carNo_col = i

    if name_col == -1 or carNo_col == -1:
        raise ValueError("表格中未找到姓名和车牌号列")

    valid_rows = []
    error_rows = []

    for row_idx, row in enumerate(table.rows[1:], start=2):
        try:
            name = row.cells[name_col].text.strip()
            car_no = row.cells[carNo_col].text.strip()

            if not name and not car_no:
                continue

            if not name or not car_no:
                error_rows.append({
                    'row': row_idx,
                    'message': f"姓名或车牌号为空 (姓名:{name}, 车牌号:{car_no})"
                })
                continue

            valid_rows.append({'name': name, 'carNo': car_no})
        except Exception as e:
            error_rows.append({'row': row_idx, 'message': str(e)})

    return valid_rows, error_rows
