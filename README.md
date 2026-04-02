<div align="center">
  <h1>Horários</h1>

  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
  <img src="https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white">
</div>

<p align="right">
API em Python (FastAPI) para consulta de horários escolares e turnos de permanência, alimentada por um banco de dados MySQL.
</p>

## Funcionalidades

- **Consultar aulas por turma ou professor**: Permite buscar todas as matérias e ver quem lecionará em cada bloco e para qual turma.
- **Autenticação**: Implementação de cadastro simplificado e login através de tokens **JWT** e senhas com geração de hash pelo **Bcrypt**. Suporte a controle de rotas por perfis de acesso (ex.: administrador e professor).
- **Detecção de Conflitos**: Ao registrar novas aulas, ocorre uma verificação em tempo real para impedir alocação dupla de turma ou professor no mesmo horário.
- **Gerenciamento Completo (CRUD)**: Endpoints com métodos `GET`, `POST`, `PUT` e `DELETE` disponíveis para professores, matérias, cursos e aulas.
- **Alimentação automatizada**: Importação direta de planilhas CSV para as tabelas relacionais do banco através de script auxiliar.

## Estrutura do Projeto

O projeto adota uma divisão lógica separando o sistema central da API (`backend/`) da interface gráfica (futura implementação).

```text
horarios/
│
├── .gitignore
├── backend/
│   ├── dados/
│   │   ├── aula_professor.csv
│   │   ├── aulas.csv
│   │   ├── materias.csv
│   │   ├── professores.csv
│   │   └── turmas.csv
│   │
│   ├── data_entry.py
│   ├── horarios.sql
│   ├── main.py
│   ├── requirements.txt
│   └── select_all.sql
│
└── README.md
```

### Tecnologias utilizadas:

- Python 3.x
- FastAPI (servidor e roteamento rápido)
- Uvicorn (servidor ASGI)
- MySQL (Armazenamento com modelagem relacional)
- mysql-connector-repackaged (Driver de comunicação DB)
- PyJWT (Tokens Bearer)
- python-bcrypt (Hash de senhas de usuários)
- Pydantic (Validação e serialização das requisições JSON)

### Arquivos

- **`dados/*.csv`**: Arquivos da base de dados estática inicial para popular rapidamente turmas, disciplinas, aulas e horários.
- **`data_entry.py`**: Script utilitário em Python encarregado de injetar os registros dos arquivos `dados/*.csv` diretamente dentro do servidor MySQL local.
- **`horarios.sql`**: Script DDL reescrito com restrições e relacionamentos profundos. Além de tabelas essenciais, agora suporta cadastro de `usuarios` (c/ tipo), controle de `cursos`, detalhes de `salas` e flexibilidade para prever restrições de horários de docentes.
- **`main.py`**: Coração da aplicação. Disponibiliza a API FastAPI com as dezenas de `endpoints` e lida tanto com segurança (login, verificação e emissão de JWTs) como validação de conflitos diretamente nas queries.
- **`requirements.txt`**: Todas as bibliotecas exigidas para garantir total compatibilidade na inicialização.
- **`select_all.sql`**: Queries básicas de verificação (`SELECT *`) para facilitar auditoria rápida nas tabelas recém-criadas.

## Como Executar

1. **Banco de Dados**: Usando uma ferramenta ou pelo servidor local MySQL, aplique o código contido em `backend/horarios.sql` para garantir a criação limpa de todos os esquemas.
2. **Dependências**: Navegue até o diretório do backend e instale os pacotes:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Carga Inicial**: Para evitar que o sistema inicie vazio, realize o preenchimento automático das planilhas:
   ```bash
   python data_entry.py
   ```
4. **Executando a API**: Inicialize a aplicação, ela disponibilizará os endpoints na porta padrão localhost:
   ```bash
   python main.py
   ```
5. **Autenticação e Testes da Interface (Swagger)**: Diferente de versões anteriores, atente-se à restrição dos painéis via `@app.post('/login')`. Utilize `http://localhost:8000/docs` para interagir com os testes do FastAPI, registrar seu usuário (`/users`) e inserir credenciais e o token pelo Authorization Header visualmente na tela de documentação via endpoint `Login`.

