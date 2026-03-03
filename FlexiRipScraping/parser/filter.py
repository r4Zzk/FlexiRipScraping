def filtrar_campos(registros, claves):
    filtrados = []

    for r in registros:
        nuevo = {k: v for k, v in r.items() if k in claves}
        filtrados.append(nuevo)

    return filtrados        


def campos_importantes(registros):
    claves_fijas = {
        'evento',
        'archivo',
        'tipo_de_trabajo',
        'dimensión',
        'resolución',
        'número_de_copias',
        'fecha_de_envío',
        'fecha_y_hora_de_inicio_de_la_salida',
        'fecha_y_hora_de_finalización_de_la_salida',
        'duración_de_la_salida',
        'tipo_archivo',
        'perfil_icc_de_salida',
        'fecha_y_hora_de_inicio_de_rip',
        'info',
        'fecha_y_hora_de_finalización_de_rip',
        'duración_de_rip',
    }
    return filtrar_campos(registros, claves_fijas)