# === filtro_keywords.py ===
from rapidfuzz import fuzz
import unicodedata

STOPWORDS = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del',
             'y', 'o', 'a', 'en', 'por', 'para', 'con', 'que', 'como', 'cuando',
             'es', 'al', 'se', 'su', 'sus', 'lo', 'le', 'les', 'este', 'esta'}

def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

def extraer_keywords(texto):
    palabras = normalizar_texto(texto).split()
    return [p for p in palabras if p not in STOPWORDS]

def calcular_similitud(palabra_usuario, palabra_pregunta):
    return fuzz.ratio(palabra_usuario, palabra_pregunta) / 100

def emparejar_keywords(keywords_usuario, keywords_pregunta):
    asignaciones = []
    usados_pregunta = set()
    similitudes_individuales = []

    for ku in keywords_usuario:
        mejor_similitud = 0
        mejor_idx = -1
        for idx, kp in enumerate(keywords_pregunta):
            if idx in usados_pregunta:
                continue
            similitud = calcular_similitud(ku, kp)
            if similitud > mejor_similitud:
                mejor_similitud = similitud
                mejor_idx = idx

        if mejor_idx >= 0:
            usados_pregunta.add(mejor_idx)
            asignaciones.append(mejor_similitud)
            similitudes_individuales.append(mejor_similitud)

    promedio = sum(asignaciones) / len(asignaciones) if asignaciones else 0
    max_similitud = max(similitudes_individuales) if similitudes_individuales else 0

    return promedio, max_similitud

def filtrar_preguntas_por_keywords(mensaje_usuario, preguntas_con_keywords, umbral=0.6, umbral_individual=0.85, debug=False):
    """
    - umbral: umbral promedio de similitud para filtrar.
    - umbral_individual: si al menos una keyword supera este valor, se incluye la pregunta.
    """
    keywords_usuario = extraer_keywords(mensaje_usuario)
    if not keywords_usuario:
        return []

    preguntas_filtradas = []

    for item in preguntas_con_keywords:
        pregunta = item['pregunta']
        keywords_pregunta = [normalizar_texto(k) for k in item.get('keywords', []) if k is not None]
        promedio, max_similitud = emparejar_keywords(keywords_usuario, keywords_pregunta)

        if debug:
            print(f"🔍 [{pregunta}] -> Promedio: {promedio:.2f}, Máxima similitud: {max_similitud:.2f}")

        if promedio >= umbral or max_similitud >= umbral_individual:
            preguntas_filtradas.append(pregunta)

    return preguntas_filtradas
