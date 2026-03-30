from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mysql.connector import pooling, Error
from pydantic import BaseModel
from typing import List, Optional
import jwt
import bcrypt
from datetime import datetime, timedelta


SECRET = 'SECRET_KEY'
ALGO = 'HS256'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

pool = pooling.MySQLConnectionPool(
    pool_name='mypool',
    pool_size=5,
    host='localhost',
    user='root',
    password='',
    database='horarios'
)

security = HTTPBearer()


def get_db():
    try:
        return pool.get_connection()
    except Error:
        raise HTTPException(500, 'Erro no banco')


def create_token(data: dict):
    payload = data.copy()
    payload['exp'] = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=[ALGO])
        return payload
    except:
        raise HTTPException(401, 'Token inválido')


class Login(BaseModel):
    username: str
    password: str

class AulaCreate(BaseModel):
    turma_id: int
    materia_id: Optional[int] = None
    professores: List[int]
    dia_semana: int
    hora_inicio: str
    hora_fim: str
    subturma: Optional[str] = None
    sala_id: Optional[int] = None

class Nome(BaseModel):
    nome: str


def conflito_horario(cur, escola_id, turma_id, professores, dia, hi, hf):
    cur.execute('''
        SELECT 1 FROM aulas
        WHERE escola_id=%s AND turma_id=%s AND dia_semana=%s
        AND (%s < hora_fim AND %s > hora_inicio)
    ''', (escola_id, turma_id, dia, hi, hf))

    if cur.fetchone():
        return 'Conflito de turma'

    for p in professores:
        cur.execute('''
            SELECT 1 FROM aulas a
            JOIN aula_professor ap ON a.id=ap.aula_id
            WHERE a.escola_id=%s AND ap.professor_id=%s AND a.dia_semana=%s
            AND (%s < a.hora_fim AND %s > a.hora_inicio)
        ''', (escola_id, p, dia, hi, hf))

        if cur.fetchone():
            return f'Conflito professor {p}'

    return None


def conflito_restricoes(cur, escola_id, turma_id, professores, dia, hi, hf):
    cur.execute('''
        SELECT 1 FROM restricoes_turma
        WHERE escola_id=%s AND turma_id=%s AND dia_semana=%s
        AND (%s < hora_fim AND %s > hora_inicio)
    ''', (escola_id, turma_id, dia, hi, hf))

    if cur.fetchone():
        return 'Restrição de turma'

    for p in professores:
        cur.execute('''
            SELECT 1 FROM restricoes_professor
            WHERE escola_id=%s AND professor_id=%s AND dia_semana=%s
            AND (%s < hora_fim AND %s > hora_inicio)
        ''', (escola_id, p, dia, hi, hf))

        if cur.fetchone():
            return f'Restrição professor {p}'

    return None


@app.post('/login')
def login(data: Login):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute('SELECT * FROM usuarios WHERE username=%s', (data.username,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user or not bcrypt.checkpw(data.password.encode(), user['password_hash'].encode()):
        raise HTTPException(401, 'Credenciais inválidas')

    token = create_token({
        'user_id': user['id'],
        'escola_id': user['escola_id'],
        'role': user['role']
    })

    return {'token': token}


@app.post('/professores')
def criar_professor(data: Nome, user=Depends(verify_token)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO professores (escola_id, nome) VALUES (%s,%s)',
        (user['escola_id'], data.nome)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {'ok': True}


@app.post('/materias')
def criar_materia(data: Nome, user=Depends(verify_token)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO materias (escola_id, nome) VALUES (%s,%s)',
        (user['escola_id'], data.nome)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {'ok': True}


@app.post('/cursos')
def criar_curso(data: Nome, user=Depends(verify_token)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO cursos (escola_id, nome) VALUES (%s,%s)',
        (user['escola_id'], data.nome)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {'ok': True}


@app.post('/aulas')
def criar_aula(data: AulaCreate, user=Depends(verify_token)):
    conn = get_db()
    cur = conn.cursor()

    escola_id = user['escola_id']

    err = conflito_horario(cur, escola_id, data.turma_id, data.professores,
                           data.dia_semana, data.hora_inicio, data.hora_fim)
    if err:
        raise HTTPException(400, err)

    err = conflito_restricoes(cur, escola_id, data.turma_id, data.professores,
                              data.dia_semana, data.hora_inicio, data.hora_fim)
    if err:
        raise HTTPException(400, err)

    cur.execute('''
        INSERT INTO aulas (
            escola_id, turma_id, materia_id,
            dia_semana, hora_inicio, hora_fim,
            subturma, sala_id
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    ''', (
        escola_id, data.turma_id, data.materia_id,
        data.dia_semana, data.hora_inicio, data.hora_fim,
        data.subturma, data.sala_id
    ))

    aula_id = cur.lastrowid

    for p in data.professores:
        cur.execute(
            'INSERT INTO aula_professor (aula_id, professor_id) VALUES (%s,%s)',
            (aula_id, p)
        )

    conn.commit()
    cur.close()
    conn.close()

    return {'id': aula_id}


@app.get('/aulas')
def listar_aulas(
    dia: Optional[int] = Query(None, ge=1, le=5),
    user=Depends(verify_token)
):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    where = ['a.escola_id=%s']
    params = [user['escola_id']]

    if dia:
        where.append('a.dia_semana=%s')
        params.append(dia)

    cur.execute(f'''
        SELECT a.*, GROUP_CONCAT(p.nome) professores
        FROM aulas a
        LEFT JOIN aula_professor ap ON a.id=ap.aula_id
        LEFT JOIN professores p ON ap.professor_id=p.id
        WHERE {' AND '.join(where)}
        GROUP BY a.id
        ORDER BY a.dia_semana, a.hora_inicio
    ''', tuple(params))

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result


@app.delete('/aulas/{id}')
def deletar_aula(id: int, user=Depends(verify_token)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        'DELETE FROM aulas WHERE id=%s AND escola_id=%s',
        (id, user['escola_id'])
    )

    conn.commit()
    cur.close()
    conn.close()

    return {'ok': True}


@app.get('/')
def root():
    return {'status': 'ok'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', reload=True)