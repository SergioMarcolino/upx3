# Calculadora de Consumo Energético

Este projeto é uma calculadora simples de consumo energético mensal, desenvolvida utilizando **HTML**, **CSS**, **JavaScript** e **Flask** no backend.

O usuário pode informar os gastos de energia (em kWh) mês a mês e calcular a média automaticamente.

---

## Funcionalidades

- Adicionar consumo mensal de energia.
- Exibir lista de gastos adicionados.
- Calcular a média de consumo energético.
- Exibir a média no navegador sem recarregar a página (requisição assíncrona).

---

## Tecnologias Utilizadas

- [Flask](https://flask.palletsprojects.com/) (Python)
- HTML5
- CSS3
- JavaScript

---
##Criacao do banco de dados sql server

CREATE TABLE usuarios (
    id INT PRIMARY KEY IDENTITY(1,1),
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(512) NOT NULL
);

CREATE TABLE consumo (
    id INT PRIMARY KEY IDENTITY(1,1),
    usuario_id INT NOT NULL,
    ano INT NOT NULL,
    mes VARCHAR(20) NOT NULL,
    consumo_kwh FLOAT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE media_estadual (
    id INT PRIMARY KEY IDENTITY(1,1),
    estado CHAR(2) NOT NULL,
    ano INT NOT NULL,
    media_kwh FLOAT NOT NULL
);
