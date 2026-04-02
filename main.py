from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mysql.connector import pooling, Error
from pydantic import BaseModel
from typing import List, Optional
import jwt
import bcrypt
from datetime import datetime, timedelta

SECRET = 'Davisao-Miseravel-Pecador'
ALGO = 'HS256'

app = FastAPI(title='Horarios', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

pool = pooling.MySQLConnectionPool(
    pool_name='mypool',
    pool_size=4,
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

def create_token(data):
    payload = data.copy()
    payload['exp'] = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try: return jwt.decode(credentials.credentials, SECRET, algorithms=[ALGO])
    except: raise HTTPException(401, 'Token invalido')

def admin_required(user=Depends(verify_token)):
    if user.get('tipo') != 'admin':
        raise HTTPException(403, 'Acesso negado')
    return user


class Login(BaseModel):
    email: str
    password: str

class AddUser(BaseModel):
    email: str
    password: str
    tipo: str
    professor_id: Optional[int] = None

class Nome(BaseModel):
    nome: str

class AulaCreate(BaseModel):
    turma_id: int
    materia_id: Optional[int] = None
    professores: List[int]
    dia_semana: int
    hora_inicio: str
    hora_fim: str
    subturma: Optional[str] = None
    sala_id: Optional[int] = None


@app.post('/login')
def login(data: Login):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM usuarios WHERE email=%s', (data.email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user or not bcrypt.checkpw(data.password.encode(), user['password_hash'].encode()):
        raise HTTPException(401, 'Credenciais invalidas')

    token = create_token({'user_id': user['id'], 'tipo': user['tipo']})
    return {'token': token}


@app.post('/users')
def add_user(data: AddUser, user=Depends(admin_required)):
    if data.tipo not in ['admin', 'professor']:
        raise HTTPException(400, 'Tipo invalido')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT id FROM usuarios WHERE email=%s', (data.email,))
    if cursor.fetchone():
        raise HTTPException(400, 'Email ja existe')

    password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

    cursor.execute(
        'INSERT INTO usuarios (email, password_hash, tipo) VALUES (%s,%s,%s)',
        (data.email, password_hash, data.tipo)
    )

    user_id = cursor.lastrowid

    if data.tipo == 'professor':
        if not data.professor_id:
            raise HTTPException(400, 'professor_id obrigatorio')

        cursor.execute('SELECT id, usuario_id FROM professores WHERE id=%s', (data.professor_id,))
        prof = cursor.fetchone()
        if not prof or prof['usuario_id']:
            raise HTTPException(400, 'Professor invalido')

        cursor.execute(
            'UPDATE professores SET usuario_id=%s WHERE id=%s',
            (user_id, data.professor_id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    return {'id': user_id}


@app.get('/professores')
def listar_professores():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM professores')
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res


@app.post('/professores')
def criar_professor(data: Nome, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO professores (nome) VALUES (%s)', (data.nome,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.put('/professores/{id}')
def atualizar_professor(id: int, data: Nome, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE professores SET nome=%s WHERE id=%s', (data.nome, id))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.delete('/professores/{id}')
def deletar_professor(id: int, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM professores WHERE id=%s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.get('/materias')
def listar_materias():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM materias')
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res


@app.post('/materias')
def criar_materia(data: Nome, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO materias (nome) VALUES (%s)', (data.nome,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.put('/materias/{id}')
def atualizar_materia(id: int, data: Nome, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE materias SET nome=%s WHERE id=%s', (data.nome, id))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.delete('/materias/{id}')
def deletar_materia(id: int, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM materias WHERE id=%s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.get('/cursos')
def listar_cursos():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM cursos')
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res


@app.post('/cursos')
def criar_curso(data: Nome, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cursos (nome) VALUES (%s)', (data.nome,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.put('/cursos/{id}')
def atualizar_curso(id: int, data: Nome, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE cursos SET nome=%s WHERE id=%s', (data.nome, id))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.delete('/cursos/{id}')
def deletar_curso(id: int, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cursos WHERE id=%s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


def conflito_horario(cursor, turma_id, professores, dia, hi, hf):
    cursor.execute(
        'SELECT 1 FROM aulas WHERE turma_id=%s AND dia_semana=%s AND (%s < hora_fim AND %s > hora_inicio)',
        (turma_id, dia, hi, hf)
    )
    if cursor.fetchone():
        return 'Conflito turma'

    for p in professores:
        cursor.execute(
            'SELECT 1 FROM aulas a JOIN aula_professor ap ON a.id=ap.aula_id WHERE ap.professor_id=%s AND a.dia_semana=%s AND (%s < a.hora_fim AND %s > a.hora_inicio)',
            (p, dia, hi, hf)
        )
        if cursor.fetchone():
            return 'Conflito professor'

    return None


@app.get('/aulas')
def listar_aulas(dia: Optional[int] = None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if dia:
        cursor.execute(
            'SELECT * FROM aulas WHERE dia_semana=%s ORDER BY hora_inicio',
            (dia,)
        )
    else:
        cursor.execute(
            'SELECT * FROM aulas ORDER BY dia_semana, hora_inicio'
        )

    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res


@app.post('/aulas')
def criar_aula(data: AulaCreate, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()

    err = conflito_horario(cursor, data.turma_id, data.professores, data.dia_semana, data.hora_inicio, data.hora_fim)
    if err:
        raise HTTPException(400, err)

    cursor.execute(
        'INSERT INTO aulas (turma_id, materia_id, dia_semana, hora_inicio, hora_fim, subturma, sala_id) VALUES (%s,%s,%s,%s,%s,%s,%s)',
        (data.turma_id, data.materia_id, data.dia_semana, data.hora_inicio, data.hora_fim, data.subturma, data.sala_id)
    )

    aula_id = cursor.lastrowid

    for p in data.professores:
        cursor.execute(
            'INSERT INTO aula_professor (aula_id, professor_id) VALUES (%s,%s)',
            (aula_id, p)
        )

    conn.commit()
    cursor.close()
    conn.close()

    return {'id': aula_id}


@app.delete('/aulas/{id}')
def deletar_aula(id: int, user=Depends(admin_required)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM aulas WHERE id=%s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'ok': True}


@app.get('/')
def root():
    return {'status': 'ok'}


if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0')