from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mysql.connector import connect, Error
from typing import Optional, List

app = FastAPI(title='API de Horários Escolares')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'horarios',
    'charset': 'utf8mb4'
}


def get_db_connection():
    try:
        return connect(**db_config)
    except Error:
        raise HTTPException(500, 'Erro no banco')


def formatar_hora(h):
    return str(h)[:-3] if h else None


def parse_turma(turma_str: str):
    try:
        serie, curso, letra, subturma = turma_str.split('_')
        return int(serie), curso, letra, subturma
    except:
        raise HTTPException(400, 'Formato inválido de turma')


BASE_QUERY = '''
    SELECT
        a.id,
        a.dia_semana,
        a.hora_inicio,
        a.hora_fim,
        m.nome as materia,
        GROUP_CONCAT(p.nome SEPARATOR ', ') as professores,
        t.serie,
        t.curso,
        t.letra,
        a.subturma
    FROM aulas a
    JOIN turmas t ON a.turma_id = t.id
    JOIN materias m ON a.materia_id = m.id
    LEFT JOIN aula_professor ap ON a.id = ap.aula_id
    LEFT JOIN professores p ON ap.professor_id = p.id
'''


@app.get('/')
def root():
    return {'status': 'ok', 'docs': '/docs'}


@app.get('/aulas')
def todas_aulas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = BASE_QUERY + ' GROUP BY a.id ORDER BY a.dia_semana, a.hora_inicio'
        cursor.execute(query)
        aulas = cursor.fetchall()

        for a in aulas:
            a['hora_inicio'] = formatar_hora(a['hora_inicio'])
            a['hora_fim'] = formatar_hora(a['hora_fim'])

        return aulas

    finally:
        cursor.close()
        conn.close()


@app.get('/professores')
def listar_professores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT nome FROM professores ORDER BY nome')
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get('/turmas')
def listar_turmas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT serie, curso, letra FROM turmas')
        turmas = cursor.fetchall()

        for t in turmas:
            t['turma'] = f"{t['serie']}_{t['curso']}_{t['letra']}"

        return turmas
    finally:
        cursor.close()
        conn.close()


@app.get('/cursos')
def listar_cursos():
    return ['EM']


@app.get('/aulas/turma')
def aulas_por_turma(
    turma: str = Query(...),
    dia: Optional[int] = Query(None, ge=1, le=5),
    subturma: Optional[str] = None
):
    serie, curso, letra, sub = parse_turma(turma)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = BASE_QUERY + '''
            WHERE t.serie=%s AND t.curso=%s AND t.letra=%s
        '''
        params = [serie, curso, letra]

        if dia is not None:
            query += ' AND a.dia_semana=%s'
            params.append(dia)

        if subturma:
            query += ' AND (a.subturma=%s OR a.subturma IS NULL)'
            params.append(subturma)

        query += ' GROUP BY a.id ORDER BY a.dia_semana, a.hora_inicio'

        cursor.execute(query, tuple(params))
        aulas = cursor.fetchall()

        for a in aulas:
            a['hora_inicio'] = formatar_hora(a['hora_inicio'])
            a['hora_fim'] = formatar_hora(a['hora_fim'])

        return aulas

    finally:
        cursor.close()
        conn.close()


@app.get('/aulas/professor')
def aulas_por_professor(
    professor: str,
    dia: Optional[int] = Query(None, ge=1, le=5),
    subturma: Optional[str] = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = BASE_QUERY + '''
            WHERE p.nome LIKE %s
        '''
        params = [f'%{professor}%']

        if dia is not None:
            query += ' AND a.dia_semana=%s'
            params.append(dia)

        if subturma:
            query += ' AND (a.subturma=%s OR a.subturma IS NULL)'
            params.append(subturma)

        query += ' GROUP BY a.id ORDER BY a.dia_semana, a.hora_inicio'

        cursor.execute(query, tuple(params))
        aulas = cursor.fetchall()

        for a in aulas:
            a['hora_inicio'] = formatar_hora(a['hora_inicio'])
            a['hora_fim'] = formatar_hora(a['hora_fim'])

        return aulas

    finally:
        cursor.close()
        conn.close()


@app.get('/entrada-saida/turma')
def entrada_saida_turma(turma: str):
    serie, curso, letra, _ = parse_turma(turma)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = '''
            SELECT
                a.dia_semana,
                MIN(a.hora_inicio) entrada,
                MAX(a.hora_fim) saida
            FROM aulas a
            JOIN turmas t ON a.turma_id=t.id
            WHERE t.serie=%s AND t.curso=%s AND t.letra=%s
            GROUP BY a.dia_semana
            ORDER BY a.dia_semana
        '''

        cursor.execute(query, (serie, curso, letra))
        res = cursor.fetchall()

        for r in res:
            r['entrada'] = formatar_hora(r['entrada'])
            r['saida'] = formatar_hora(r['saida'])

        return res

    finally:
        cursor.close()
        conn.close()


@app.get('/entrada-saida/professor')
def entrada_saida_professor(professor: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = '''
            SELECT
                a.dia_semana,
                MIN(a.hora_inicio) entrada,
                MAX(a.hora_fim) saida
            FROM aulas a
            JOIN aula_professor ap ON a.id=ap.aula_id
            JOIN professores p ON ap.professor_id=p.id
            WHERE p.nome LIKE %s
            GROUP BY a.dia_semana
            ORDER BY a.dia_semana
        '''

        cursor.execute(query, (f'%{professor}%',))
        res = cursor.fetchall()

        for r in res:
            r['entrada'] = formatar_hora(r['entrada'])
            r['saida'] = formatar_hora(r['saida'])

        return res

    finally:
        cursor.close()
        conn.close()


@app.get('/juntos')
def juntos(
    professores: Optional[List[str]] = Query(None),
    turmas: Optional[List[str]] = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        filtros = []
        params = []

        if professores:
            filtros.append('p.nome IN (%s)' % ','.join(['%s'] * len(professores)))
            params.extend(professores)

        if turmas:
            conds = []
            for t in turmas:
                serie, curso, letra, _ = parse_turma(t)
                conds.append('(t.serie=%s AND t.curso=%s AND t.letra=%s)')
                params.extend([serie, curso, letra])
            filtros.append('(' + ' OR '.join(conds) + ')')

        where = ('WHERE ' + ' OR '.join(filtros)) if filtros else ''

        query = BASE_QUERY + f'''
            {where}
            GROUP BY a.id
            ORDER BY a.dia_semana, a.hora_inicio
        '''

        cursor.execute(query, tuple(params))
        res = cursor.fetchall()

        for r in res:
            r['hora_inicio'] = formatar_hora(r['hora_inicio'])
            r['hora_fim'] = formatar_hora(r['hora_fim'])

        return res

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    from uvicorn import run
    run('main:app', host='0.0.0.0', reload=True)