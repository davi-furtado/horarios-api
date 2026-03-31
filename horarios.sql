DROP DATABASE IF EXISTS horarios;
CREATE DATABASE horarios
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE horarios;

CREATE TABLE escolas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);


CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'professor') NOT NULL,

    UNIQUE (escola_id, username),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE
);


CREATE TABLE professores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    usuario_id INT,

    UNIQUE (escola_id, nome),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,

    FULLTEXT (nome)
);


CREATE TABLE materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,

    UNIQUE (escola_id, nome),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE,

    FULLTEXT (nome)
);


CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,

    UNIQUE (escola_id, nome),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE,

    FULLTEXT (nome)
);


CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('sala', 'lab', 'quadra', 'outro') DEFAULT 'sala' NOT NULL,

    UNIQUE (escola_id, nome),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE,

    FULLTEXT (nome),
    INDEX idx_salas_tipo (tipo)
);


CREATE TABLE turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    serie TINYINT UNSIGNED,
    curso_id INT NOT NULL,
    letra CHAR(1),
    sala_id INT,

    CHECK (serie IS NULL OR serie BETWEEN 1 AND 10),

    UNIQUE (escola_id, serie, curso_id, letra),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE,
    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE SET NULL,

    INDEX idx_turma_curso (curso_id),
    INDEX idx_turma_serie (serie)
);


CREATE TABLE aulas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    turma_id INT NOT NULL,
    materia_id INT,

    dia_semana TINYINT UNSIGNED NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    subturma CHAR(1),
    sala_id INT,

    CHECK (dia_semana BETWEEN 1 AND 5),
    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE,
    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
    FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE SET NULL,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE SET NULL,

    INDEX idx_aulas_turma (turma_id),
    INDEX idx_aulas_dia (dia_semana),
    INDEX idx_aulas_horario (hora_inicio, hora_fim)
);


CREATE TABLE aula_professor (
    aula_id INT,
    professor_id INT,

    PRIMARY KEY (aula_id, professor_id),

    FOREIGN KEY (aula_id) REFERENCES aulas(id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE,

    INDEX idx_ap_professor (professor_id)
);


CREATE TABLE restricoes_professor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    professor_id INT NOT NULL,

    dia_semana TINYINT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE,

    INDEX idx_rp_prof (professor_id),
    INDEX idx_rp_dia (dia_semana)
);


CREATE TABLE restricoes_turma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    escola_id INT NOT NULL,
    turma_id INT NOT NULL,

    dia_semana TINYINT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE,
    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,

    INDEX idx_rt_turma (turma_id),
    INDEX idx_rt_dia (dia_semana)
);