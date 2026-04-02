DROP DATABASE IF EXISTS horarios;
CREATE DATABASE horarios
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE horarios;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'professor') NOT NULL
);

CREATE TABLE professores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    usuario_id INT UNIQUE,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,

    INDEX idx_prof_nome (nome)
);

CREATE TABLE materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE professor_materia (
    professor_id INT,
    materia_id INT,

    PRIMARY KEY (professor_id, materia_id),

    FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE,
    FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
);

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    tipo ENUM('sala', 'lab', 'quadra', 'outro') NOT NULL DEFAULT 'sala',

    INDEX idx_salas_tipo (tipo)
);

CREATE TABLE turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serie TINYINT UNSIGNED,
    curso_id INT NOT NULL,
    letra CHAR(1),
    sala_id INT,

    CHECK (serie IS NULL OR serie >= 1),

    UNIQUE (serie, curso_id, letra),

    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE SET NULL,

    INDEX idx_turma_curso (curso_id),
    INDEX idx_turma_serie (serie)
);

CREATE TABLE aulas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    turma_id INT NOT NULL,
    materia_id INT NOT NULL,
    dia_semana TINYINT UNSIGNED NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    subturma CHAR(1),
    sala_id INT NOT NULL,

    CHECK (dia_semana BETWEEN 1 AND 5),
    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
    FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE CASCADE,

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

CREATE TABLE restricoes_curso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    dia_semana TINYINT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    CHECK (dia_semana BETWEEN 1 AND 5),
    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,

    INDEX idx_rc_curso (curso_id),
    INDEX idx_rc_dia (dia_semana)
);

CREATE TABLE restricoes_professor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    professor_id INT NOT NULL,
    dia_semana TINYINT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    CHECK (dia_semana BETWEEN 1 AND 5),
    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE,

    INDEX idx_rp_prof (professor_id),
    INDEX idx_rp_dia (dia_semana)
);