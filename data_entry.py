from mysql.connector import connect
from csv import DictReader, DictWriter

DATA_DIR = 'dados/'

def ler_escrever(path, lambda_key):
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


def truncate(table):
    cursor.execute(f'TRUNCATE TABLE {table}')


professores = ler_escrever('professores', lambda x: x['nome'])
turmas = ler_escrever('turmas', lambda x: x['curso'])
materias = ler_escrever('materias', lambda x: x['nome'])
aulas = ler_escrever('aulas', lambda x: (x['turma_id'], x['dia_semana'], x['hora_inicio'], x['subturma']))
aula_professor = ler_escrever('aula_professor', lambda x: x['professor_id'])

connection = connect(
    host='localhost',
    user='root',
    password='',
    database='horarios',
    charset='utf8mb4'
)
cursor = connection.cursor(dictionary=True)

cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
cursor.execute('TRUNCATE TABLE professores')
cursor.execute('TRUNCATE TABLE turmas')
cursor.execute('TRUNCATE TABLE materias')
cursor.execute('TRUNCATE TABLE aulas')
cursor.execute('TRUNCATE TABLE aula_professor')
cursor.execute('SET FOREIGN_KEY_CHECKS = 1')

connection.commit()

inserir('professores', professores)
inserir('turmas', turmas)
inserir('materias', materias)
inserir('aulas', aulas)
inserir('aula_professor', aula_professor)

connection.commit()

cursor.close()
connection.close()