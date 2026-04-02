import bcrypt
from mysql.connector import connect
from csv import DictReader, DictWriter

DATA_DIR = 'dados/'

def ler_ordenar(path, lambda_key):
    arquivo = f'{DATA_DIR}{path}.csv'

    with open(arquivo, 'r', encoding='utf-8') as f:
        reader = DictReader(f)
        fieldnames = reader.fieldnames
        dados = sorted(reader, key=lambda_key)

    with open(arquivo, 'w', encoding='utf-8', newline='') as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dados)

    return dados


def inserir(tabela, dados):
    if not dados: return

    colunas = list(dados[0].keys())
    placeholders = ', '.join(['%s'] * len(colunas))
    colunas_sql = ', '.join(colunas)

    sql = f'INSERT INTO {tabela} ({colunas_sql}) VALUES ({placeholders})'

    valores = [
        tuple(linha[col] if linha[col] != '' else None for col in colunas)
        for linha in dados
    ]

    cursor.executemany(sql, valores)


usuarios = ler_ordenar('usuarios', lambda x: (x['tipo'], x['email']))
for x in usuarios:
    x['password_hash'] = bcrypt.hashpw(x['password_hash'].encode(), bcrypt.gensalt()).decode()
professores = ler_ordenar('professores', lambda x: x['nome'])
materias = ler_ordenar('materias', lambda x: x['nome'])
professor_materia = ler_ordenar('professor_materia', lambda x: (x['professor_id'], x['materia_id']))
cursos = ler_ordenar('cursos', lambda x: x['nome'])
salas = ler_ordenar('salas', lambda x: x['nome'])
turmas = ler_ordenar(
    'turmas',
    lambda x: (
        x['serie'],
        x['curso_id'],
        x['letra'] or ''
    )
)
aulas = ler_ordenar(
    'aulas',
    lambda x: (
        x['turma_id'],
        x['dia_semana'],
        x['hora_inicio'],
        x['subturma'] or ''
    )
)
aula_professor = ler_ordenar('aula_professor', lambda x: x['aula_id'])
restricoes_curso = ler_ordenar(
    'restricoes_curso',
    lambda x: (
        x['curso_id'],
        x['dia_semana'],
        x['hora_inicio']
    )
)
restricoes_professor = ler_ordenar(
    'restricoes_professor',
    lambda x: (
        x['professor_id'],
        x['dia_semana'],
        x['hora_inicio']
    )
)


connection = connect(
    host='localhost',
    user='root',
    password='',
    database='horarios',
    charset='utf8mb4'
)
cursor = connection.cursor(dictionary=True)


inserir('usuarios', usuarios)
inserir('professores', professores)
inserir('materias', materias)
inserir('professor_materia', professor_materia)
inserir('cursos', cursos)
inserir('salas', salas)
inserir('turmas', turmas)
inserir('aulas', aulas)
inserir('aula_professor', aula_professor)
inserir('restricoes_curso', restricoes_curso)
inserir('restricoes_professor', restricoes_professor)


connection.commit()

cursor.close()
connection.close()