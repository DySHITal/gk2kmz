CSV_HELP = (
    "**Columnas requeridas** (fila de encabezado, en minúsculas): `name`, `este`, `norte`\n\n"
    "**Ejemplo:**\n\n"
    "`name,este,norte`\n\n"
    "`P1,3393954.90,7347028.14`\n\n"
    "`P2,3393990.25,7347100.60`\n\n"
    "- Separador: coma o punto y coma\n"
    "- Decimales: punto, sin separador de miles\n"
    "- Los valores son metros Gauss-Krüger, del datum y la faja elegidos arriba\n"
    "- Si `name` está vacío, se asigna un nombre automático\n"
    "- Las filas con `este` o `norte` vacíos se omiten\n"
    "- Polígono: ordená los puntos siguiendo el perímetro y no repitas el primero al final"
)

CSV_TEMPLATE = "name,este,norte\nP1,3393954.90,7347028.14\nP2,3393990.25,7347100.60\n"