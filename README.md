<div align="center">
<h1>Horários</h1>

  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
  <img src="https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white">
</div>

<p align="right">
Sistema interativo de terminal (CLI) em Python para consulta de horários escolares e turnos de permanência, alimentado por um banco de dados MySQL.
</p>

# Funcionalidades

- **Consultar aulas por turma ou professor**: Permite buscar todas as matérias e ver quem lecionará em cada bloco e para qual turma.
- **Checar horários de permanência**: Informa de maneira simplificada a hora exata da primeira aula (entrada) e última aula (saída), muito útil para gestão escolar.
- **Filtros dinâmicos**: O usuário pode optar por filtrar a visualização por um dia específico da semana, ou exibir o quadro geral de segunda a sexta.
- **Alimentação automatizada**: Importação direta de planilhas CSV para as tabelas relacionais do banco através de script auxiliar.

# Estrutura do Projeto

```text
horarios/
│
├── dados/
│   ├── aula_professor.csv
│   ├── aulas.csv
│   ├── professores.csv
│   └── turmas.csv
│
├── data_entry.py
├── horarios.sql
├── LICENSE
├── main.py
└── README.md
```

## Tecnologias utilizadas:

- Python
- MySQL
- mysql-connector-python
- CSV nativo

## Arquivos

### `dados/*.csv`

Arquivos em formato **CSV** que servem como a base de dados em formato bruto. Contêm as listagens estáticas de nomenclaturas de turmas, disciplinas, vínculos de aulas com professores e horários em texto simples.

### `data_entry.py`

Script utilitário em Python responsável pela carga de dados ("Data Entry"). Ele lê as diversas planilhas contidas na pasta `dados/`, faz a ordenação pelas colunas-chave em memória, limpa o modelo ativando ou desativando chaves estrangeiras (usando os comandos `TRUNCATE` e `FOREIGN_KEY_CHECKS`) e injeta tudo de volta no servidor MySQL.

### `horarios.sql`

Script DDL para criação da estrutura relacional. Contém as modelagens iniciais: exclui o banco se ele já existir, cria e seleciona o banco `horarios` e define a configuração das tabelas necessárias (`professores`, `turmas`, `aulas` e a tabela associativa `aula_professor`), incluindo integridades referenciais (_FOREIGN KEYS_) do sistema escolar.

### `main.py`

O corpo principal da aplicação. Executado no terminal de comandos, fornece uma interface interativa via menu numérico (`while True`). As requisições são processadas em tempo real com acesso direto ao banco MySQL local. As consultas (`queries`) priorizam o uso da diretiva `GROUP_CONCAT` para agrupar as exibições em tela.

# Licença

Este projeto está sob a licença [MIT](/LICENSE)
