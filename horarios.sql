DROP DATABASE IF EXISTS horarios;
CREATE DATABASE horarios
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE horarios;

CREATE TABLE professores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serie TINYINT UNSIGNED,
    curso_id INT(100) NOT NULL,
    letra ENUM('A', 'B', 'C'),

    CHECK (serie IS NULL OR serie BETWEEN 1 AND 10),

    UNIQUE (serie, curso_id, letra),

    FOREIGN KEY curso_id REFERENCES cursos(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE aulas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    turma_id INT NOT NULL,
    materia_id INT,

    dia_semana TINYINT UNSIGNED NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    subturma ENUM('A', 'B'),

    CHECK (dia_semana BETWEEN 1 AND 5),
    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE aula_professor (
    aula_id INT,
    professor_id INT,

    PRIMARY KEY (aula_id, professor_id),

    FOREIGN KEY (aula_id) REFERENCES aulas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE ON UPDATE CASCADE
);