from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mysql.connector import connect, Error
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'horarios',
}


def get_db():
    try:
        return connect(**db_config)
    except Error:
        raise HTTPException(500, 'Erro no banco')


def fmt(h):
    return str(h)[:-3] if h else None


def parse_turma(t: str):
    partes = t.split('_')

    serie = None
    curso = None
    letra = None
    subturma = None

    for p in partes:
        if p.isdigit():
            serie = int(p)
        elif p in ['A', 'B', 'C']:
            if not letra:
                letra = p
            else:
                subturma = p
        else:
            curso = p

    if not curso:
        raise HTTPException(400, 'Curso é obrigatório')

    return serie, curso, letra, subturma


BASE = '''
SELECT
    a.id,
    a.dia_semana,
    a.hora_inicio,
    a.hora_fim,
    m.nome materia,
    GROUP_CONCAT(p.nome) professores,
    t.serie,
    c.nome curso,
    t.letra,
    a.subturma
FROM aulas a
JOIN turmas t ON a.turma_id = t.id
JOIN cursos c ON t.curso_id = c.id
JOIN materias m ON a.materia_id = m.id
LEFT JOIN aula_professor ap ON a.id = ap.aula_id
LEFT JOIN professores p ON ap.professor_id = p.id
'''


@app.get('/aulas')
def aulas(
    turma: Optional[str] = None,
    professor: Optional[str] = None,
    dia: Optional[int] = Query(None, ge=1, le=5),
    materia: Optional[str] = None,
    hora_inicio: Optional[str] = None,
):
    if not turma and not professor:
        where = ''
        params = []
    else:
        where = 'WHERE '
        params = []

        conds = []

        if turma:
            serie, curso, letra, subturma = parse_turma(turma)

            conds.append('c.nome LIKE %s')
            params.append(f'%{curso}%')

            if serie:
                conds.append('t.serie=%s')
                params.append(serie)

            if letra:
                conds.append('t.letra=%s')
                params.append(letra)

            if subturma:
                conds.append('(a.subturma IS NULL OR a.subturma=%s)')
                params.append(subturma)

        if professor:
            conds.append('p.nome LIKE %s')
            params.append(f'%{professor}%')

        where += ' AND '.join(conds)

    if dia:
        where += ' AND a.dia_semana=%s' if where else 'WHERE a.dia_semana=%s'
        params.append(dia)

    if materia:
        where += ' AND m.nome=%s' if where else 'WHERE m.nome=%s'
        params.append(materia)

    if hora_inicio:
        where += ' AND a.hora_inicio=%s' if where else 'WHERE a.hora_inicio=%s'
        params.append(hora_inicio)

    query = BASE + f'''
    {where}
    GROUP BY a.id
    ORDER BY a.dia_semana, a.hora_inicio
    '''

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, tuple(params))
        response = curso.fetchall()

        for r in response:
            r['hora_inicio'] = fmt(r['hora_inicio'])
            r['hora_fim'] = fmt(r['hora_fim'])

        return response
    finally:
        cursor.close()
        conn.close()


@app.get('/entrada-saida')
def entrada_saida(
    turma: Optional[str] = None,
    professor: Optional[str] = None,
):
    if not turma and not professor:
        raise HTTPException(400, 'Informe turma ou professor')

    where = []
    params = []

    if turma:
        serie, curso, letra, subturma = parse_turma(turma)

        where.append('c.nome LIKE %s')
        params.append(f'%{curso}%')

        if serie:
            where.append('t.serie=%s')
            params.append(serie)

        if letra:
            where.append('t.letra=%s')
            params.append(letra)
        
        if subturma:
            where.append('(a.subturma IS NULL OR a.subturma=%s)')
            params.append(subturma)

    if professor:
        where.append('p.nome LIKE %s')
        params.append(f'%{professor}%')

    query = f'''
    SELECT
        a.dia_semana,
        MIN(a.hora_inicio) entrada,
        MAX(a.hora_fim) saida
    FROM aulas a
    JOIN turmas t ON a.turma_id = t.id
    JOIN cursos c ON t.curso_id = c.id
    LEFT JOIN aula_professor ap ON a.id = ap.aula_id
    LEFT JOIN professores p ON ap.professor_id = p.id
    WHERE {" AND ".join(where)}
    GROUP BY a.dia_semana
    ORDER BY a.dia_semana
    '''

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, tuple(params))
        response = cursor.fetchall()

        for r in response:
            r['entrada'] = fmt(r['entrada'])
            r['saida'] = fmt(r['saida'])

        return response
    finally:
        cursor.close()
        conn.close()


@app.get('/conflitos')
def conflitos(
    professores: Optional[list[str]] = Query(None),
    turmas: Optional[list[str]] = Query(None),
):
    conn = get_db()
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
                serie, curso, letra, subturma = parse_turma(t)

                c = ['c.nome LIKE %s']
                params.append(f'%{curso}%')

                if serie:
                    c.append('t.serie=%s')
                    params.append(serie)

                if letra:
                    c.append('t.letra=%s')
                    params.append(letra)

                if subturma:
                    c.append('(a.subturma IS NULL OR a.subturma=%s)')
                    params.append(subturma)

                conds.append('(' + ' AND '.join(c) + ')')

            filtros.append('(' + ' OR '.join(conds) + ')')

        where = ('WHERE ' + ' OR '.join(filtros)) if filtros else ''

        query = BASE + f'''
        {where}
        GROUP BY a.id
        ORDER BY a.dia_semana, a.hora_inicio
        '''

        cursor.execute(query, tuple(params))
        response = cursor.fetchall()

        for r in response:
            r['hora_inicio'] = fmt(r['hora_inicio'])
            r['hora_fim'] = fmt(r['hora_fim'])

        return response

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    from uvicorn import run
    run('main:app', host='0.0.0.0', reload=True)