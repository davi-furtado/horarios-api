from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mysql.connector import connect, Error
from typing import Optional
from datetime import timedelta

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

BASE_QUERY = '''
    SELECT a.id, a.dia_semana, a.hora_inicio, a.hora_fim, a.materia,
           t.serie, t.curso, t.letra,
           GROUP_CONCAT(p.nome SEPARATOR ', ') as professores
    FROM aulas a
    JOIN turmas t ON a.turma_id = t.id
    LEFT JOIN aula_professor ap ON a.id = ap.aula_id
    LEFT JOIN professores p ON ap.professor_id = p.id
'''

def get_db_connection():
    try:
        return connect(**db_config)
    except Error:
        raise HTTPException(status_code=500, detail='Erro de conexão com o banco')


@app.get('/')
def read_root():
    return {'status': 'API Online', 'docs': '/docs'}

@app.get('/aulas')
def listar_aulas(
    tipo: int = Query(...),
    valor: str = Query(...),
    dia: Optional[int] = Query(None, ge=0, le=4)
):
    if tipo not in (1, 2):
        raise HTTPException(status_code=400, detail='Tipo inválido')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if tipo == 1:
            filtro_sql = 't.id = %s'
            filtro_valor = int(valor)
        else:
            filtro_sql = 'p.nome LIKE %s'
            filtro_valor = f'%{valor}%'

        query = f'{BASE_QUERY} WHERE {filtro_sql}'
        params = [filtro_valor]

        if dia is not None:
            query += ' AND a.dia_semana = %s'
            params.append(dia)

        query += ' GROUP BY a.id ORDER BY a.dia_semana, a.hora_inicio'

        cursor.execute(query, tuple(params))
        aulas = cursor.fetchall()

        if not aulas:
            raise HTTPException(status_code=404, detail='Nenhuma aula encontrada')

        for aula in aulas:
            aula['hora_inicio'] = str(aula['hora_inicio'])[:-3]
            aula['hora_fim'] = str(aula['hora_fim'])[:-3]

        return aulas

    finally:
        cursor.close()
        conn.close()

@app.get('/horarios-resumo')
def resumo_entrada_saida(
    tipo: int = Query(...),
    valor: str = Query(...),
    dia: Optional[int] = Query(None, ge=0, le=4)
):
    if tipo not in (1, 2):
        raise HTTPException(status_code=400, detail='Tipo inválido')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if tipo == 1:
            query = '''
                SELECT a.dia_semana, t.serie, t.curso, t.letra, 
                       MIN(a.hora_inicio) as entrada, MAX(a.hora_fim) as saida
                FROM aulas a
                JOIN turmas t ON a.turma_id = t.id
                WHERE t.id = %s
            '''
            filtro_valor = int(valor)
            group_by = ' GROUP BY a.dia_semana, t.id'
        else:
            query = '''
                SELECT a.dia_semana, p.nome as professor, 
                       MIN(a.hora_inicio) as entrada, MAX(a.hora_fim) as saida
                FROM aulas a
                JOIN aula_professor ap ON a.id = ap.aula_id
                JOIN professores p ON ap.professor_id = p.id
                WHERE p.nome LIKE %s
            '''
            filtro_valor = f'%{valor}%'
            group_by = ' GROUP BY a.dia_semana, p.id'

        params = [filtro_valor]

        if dia is not None:
            query += ' AND a.dia_semana = %s'
            params.append(dia)

        query += group_by + ' ORDER BY a.dia_semana'

        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()

        if not resultados:
            raise HTTPException(status_code=404, detail='Nenhum horário encontrado')

        for r in resultados:
            r['entrada'] = str(r['entrada'])[:-3]
            r['saida'] = str(r['saida'])[:-3]

            if tipo == 1:
                r['alvo'] = f"{r['serie']}º {r['curso']} {r['letra'] or ''}".strip()

        return resultados

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    from uvicorn import run
    run('main:app', host='0.0.0.0', reload=True)