def parsear_txt_a_json(ruta_txt: str) -> list:
    import re, json
    with open(ruta_txt, encoding='utf-8') as f:
        contenido = f.read()
    bloques = re.split(r'\n(?=\¿)', contenido)
    contexto = []
    for bloque in bloques:
        pregunta_match = re.search(r'\¿(.+?)\?', bloque)
        respuesta_match = re.search(r'\?\n(.+?)(?=Documentos:|$)', bloque, re.DOTALL)
        documentos_match = re.findall(r'"([^"]+),\s*([^"]+)"', bloque)
        if pregunta_match and respuesta_match:
            pregunta = pregunta_match.group(1).strip()
            respuesta = respuesta_match.group(1).strip()
            documentos = [{'nombre': d[0].strip(), 'referencia': d[1].strip()} for d in documentos_match]
            contexto.append({
                'pregunta': pregunta,
                'respuesta': respuesta,
                'documentos': documentos
            })
    return contexto