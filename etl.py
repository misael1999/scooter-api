import openpyxl
from pathlib import Path

xlsx_file = Path('inventario-minisuper.xlsx')
wb_obj = openpyxl.load_workbook(xlsx_file)
sheet = wb_obj.active
info = []


for i, row in enumerate(sheet.iter_rows(values_only=True)):
    subcategories = []
    sections = []
    data = {}
    if i == 0:
        pass
    else:

        data['name'] = row[0]
        subs = str(row[1])
        sect = str(row[2])
        subcategories_temp = subs.strip().split(',')
        sections = sect.strip().split('|')
        if len(sections) == len(subcategories_temp):
            for idx, subcategory in enumerate(subcategories_temp):
                sections_temp = sections[idx].strip().split(',')
                sub_temp = {'name': subcategory, 'sections': sections_temp}
                subcategories.append(sub_temp)
        else:
            print(subcategories_temp)
            print(len(sections))
            print(len(subcategories_temp))
            raise ValueError('La cantidad de secciones no corresponde a la cantidad de subcategorias')

        data['subcategorias'] = subcategories
        info.append(data)

print(info)
