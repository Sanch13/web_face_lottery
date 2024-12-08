from urllib.parse import quote

from django.http import HttpResponse

import pandas as pd
from openpyxl.styles import Alignment


def create_list_of_participants_lottery(data):
    columns = ['Номер', 'ФИО Участника', 'Билет']
    df = pd.DataFrame(data, columns=columns)

    # Имя файла на кириллице
    filename = "Участники_лотереи.xlsx"
    quoted_filename = quote(filename.encode('utf-8'))

    # Создаём ответ с Excel-файлом
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{quoted_filename}"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Participants')

        # Получаем доступ к листу
        worksheet = writer.sheets['Participants']

        column_settings = {
            'A': {"width": 8, "alignment": Alignment(horizontal='center')},
            'B': {"width": 32, "alignment": Alignment(horizontal='left')},
            'C': {"width": 8, "alignment": Alignment(horizontal='center')},
        }

        # Применяем настройки к колонкам
        for column, settings in column_settings.items():
            worksheet.column_dimensions[column].width = settings["width"]
            for cell in worksheet[column]:
                cell.alignment = settings["alignment"]

    return response
