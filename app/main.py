import json
import os.path
import uuid
from enum import Enum
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import pandas as pd
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()


class FormaterEnum(str, Enum):
    json2xlsx = 'json2xlsx'


class ContentRequest(BaseModel):
    formater: FormaterEnum
    content: str


FORMATER_FMT = {
    FormaterEnum.json2xlsx: 'xlsx'
}

BASE_DIR = '../files'


@app.post('/generate-file')
async def generate_file(request: ContentRequest):
    file_id = str(uuid.uuid4())
    filename = f'{file_id}.{FORMATER_FMT[request.formater]}'
    os.makedirs(BASE_DIR, exist_ok=True)
    filepath = os.path.join(BASE_DIR, filename)
    match request.formater:
        case FormaterEnum.json2xlsx:
            try:
                data = json.loads(request.content)
            except json.decoder.JSONDecodeError as e:
                raise HTTPException(400, f'json解析失败：{e}')
            df = pd.DataFrame(data['rows'], columns=data['columns'])
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='测试用例')
                worksheet = writer.sheets['测试用例']
                # 行高
                for row_idx in range(1, len(df) + 2):
                    worksheet.row_dimensions[row_idx].height = 48
                # 列宽
                for i in range(1, len(df.columns) + 1):
                    col_letter = get_column_letter(i)
                    worksheet.column_dimensions[col_letter].width = 48

                # 自动换行
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.alignment = Alignment(wrap_text=True)

            return JSONResponse({'filename': filename})
        case _:
            raise HTTPException(status_code=400, detail=f'暂不支持的转换方法：{request.formater}')


@app.get('/download-file/{filename}')
async def download_make_file(filename: str):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f'文件不存在或已删除：{filename}')
    return FileResponse(filepath)
