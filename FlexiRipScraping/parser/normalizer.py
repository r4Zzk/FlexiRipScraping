from datetime import datetime

def normalizar(datos):
    normalizados = []

    for registro in datos:
        nuevo = {}

        for k, v in registro.items():
            clave = k.strip().lower().replace(" ", "_")
            valor = v.strip()

            nuevo[clave] = valor

        normalizados.append(nuevo)

    return normalizados

## Cosas que faltan ##

#1. Normalizar fechas a ISO
#2. Convertir numeros
#3. Dimensiones
#4. Tiempo de duracion

#[
#    {
#        ✓✓✓'evento': 'Terminar trabajo RIP', 
#        'impresora': 'Inkjetprinter-HS-3200-MINI', 
#        'puerto': 'TCP/IP', 
#        ✓✓✓'archivo': 'E:\\16-8\\PABLO SCHERNESKI 16-08.tif', 
#        'tamaño': '316157.4k', 
#        'emisor': '202502', 
#        ✓✓✓'tipo_de_trabajo': 'Imprimir trabajo', 
#        ✓✓✓'tipo_archivo': 'Archivo TIFF', 
#        'tras_salida': 'Retener', 
#        ✓✓✓'dimensión': '58.0 x 100.0cm', 
#        ✓✓✓'resolución': '720.00 x 1800.00', 
#        'modo_de_color': 'CMYK(2 bits)', 
#        'tipo_de_difusión': 'Estocástico mejorado', 
#        'modo_de_renderización': 'Alta Calidad', 
#        'perfil_icc_gris': 'GRACoL2006_Coated1v2.icc', 
#        'perfil_icc_rgb': 'sRGB_IEC61966_21.icm', 
#        'perfil_cmyk_icc': 'GRACoL2006_Coated1v2.icc', 
#        ✓✓✓'perfil_icc_de_salida': 'HS-3200-Tanghua 720x1800 6PASS .icc', 
#        'bitmap_cmyk': 'Perceptual', 
#        'cmyk_vector': 'Colorimétrico Relativo', 
#        'cmyk_text': 'Colorimétrico Relativo', 
#        'cmyk_gradient': 'Colorimétrico Relativo', 
#        'bitmap_no-cmyk': 'Perceptual', 
#        'vector_no-cmyk': 'Colorimétrico Relativo', 
#        'texto_no-cmyk': 'Colorimétrico Relativo', 
#        'degradado_no-cmyk': 'Colorimétrico Relativo', 
#        'corrección_de_color': 'Sí', 
#        'usar_perfil_icc_incrustado_para_cmyk': 'Sí', 
#        'usar_perfil_icc_incrustado_para_rgb': 'Sí', 
#        'usar_perfil_icc_incrustado_para_gris': 'Sí', 
#        'usar_reasignación_de_color_plano': 'Sí', 
#        ✓✓✓'número_de_copias': '1', 
#        'número_de_panel_parcial': '1', 
#        'número_de_página': '1', 
#        ✓✓✓'fecha_de_envío': '8/13/2025 1:23 PM', 
#        'sobreposición': '0.500cm', 
#        'imprimir_etiqueta': 'Sí', 
#        'marcas_de_impresora': 'Marca desconocida', 
#        ✓✓✓'fecha_y_hora_de_inicio_de_rip': '13:26:28 13/8/2025', 
#        'tiempo_de_preparación_del_trabajo': '0.000000 sec', 
#        ✓✓✓'info': 'El trabajo fue ejecutado con éxito', 
#        ✓✓✓'fecha_y_hora_de_finalización_de_rip': '13:27:28 13/8/2025', 
#        ✓✓✓'duración_de_rip': '1 minutos 0 segundos'
#    }
#]

#[
#   {
#       ✓✓✓'evento': 'Fin de salida', 
#       'nombre_de_dispositivo': 'Inkjetprinter-HS-3200-MINI', 
#       'puerto': 'TCP/IP', 
#       ✓✓✓'archivo': 'Anidar (3 trabajos)', 
#       'tamaño': '329807,9k', 
#       'emisor': '202502', 
#       ✓✓✓'tipo_de_trabajo': 'Trabajo anidado', 
#       'tras_salida': 'Retener', 
#       ✓✓✓'dimensión': '22,8 x 19,3 in', 
#       ✓✓✓'resolución': '720x1800 6PASS', 
#       'modo_de_color': 'CMYK(2 bits)', 
#       'tipo_de_difusión': 'Estocástico mejorado', 
#       'perfil_icc_gris': 'GRACoL2006_Coated1v2.icc', 
#       'perfil_icc_rgb': 'sRGB_IEC61966_21.icm', 
#       'perfil_cmyk_icc': 'GRACoL2006_Coated1v2.icc', 
#       'perfil_icc_de_salida': 'HS-3200-Tanghua 720x1800 6PASS .icc', 
#       'renderización_bitmap_cmyk': 'Perceptual', 
#       'renderización_vectorial_cmyk': 'Colorimétrico Relativo', 
#       'renderización_de_texto_cmyk': 'Colorimétrico Relativo', 
#       'renderización_degradado_cmyk': 'Colorimétrico Relativo', 
#       'renderización_de_bitmap_no_cmyk': 'Perceptual', 
#       'renderización_vectorial_no_cmyk': 'Colorimétrico Relativo', 
#       'renderización_de_texto_no_cmyk': 'Colorimétrico Relativo', 
#       'renderización_de_degradado_no_cmyk': 'Colorimétrico Relativo', 
#       'aplicar_corrección_de_color': 'Sí', 
#       'aplicar_linearización': 'Sí', 
#       'usar_perfil_icc_incrustado_para_cmyk': 'Sí', 
#       'usar_perfil_icc_incrustado_para_rgb': 'Sí', 
#       'usar_perfil_icc_incrustado_para_gris': 'Sí', 
#       'usar_reasignación_de_color_plano': 'Sí', 
#       ✓✓✓'número_de_copias': '1', 
#       'número_de_página': '1', 
#       ✓✓✓'fecha_de_envío': '8/13/2025 1:23 PM', 
#       'sobreposición': '0,197', 
#       'imprimir_etiqueta': 'Sí', 
#       'notas_de_etiqueta': '', 
#       'imprimir_bandas_de_color': 'No', 
#       ✓✓✓'fecha_y_hora_de_inicio_de_la_salida': '13:31:16 13/8/2025', 
#       ✓✓✓'fecha_y_hora_de_finalización_de_la_salida': '13:31:34 13/8/2025', 
#       ✓✓✓'duración_de_la_salida': '18 segundos'
    #}
#]
