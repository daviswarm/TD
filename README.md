# Transmissão de Dados

Este repositório corresponde ao projeto final de programação da disciplina de Transmissão de Dados da Universidade de Brasília.

## Configurações

- Versão do Python: 3.9.5

Para definir as configurações do projeto, instale a versão do Python utilizada e o instalador de pacotes pip. Depois, siga as etapas para criação e ativação do ambiente de desenvolvimento de acordo com o seu sistema operacional na pasta **root** desse repositório.

### Clone o repositório pyDash utilizado

- No terminal, execute
```bash
git clone https://github.com/mfcaetano/pydash.git
```

### Crie um ambiente de desenvolvimento virtual

- No ambiente Windows, no bash do git, execute
```bash
python -m venv TDDash
```

- No ambiente Linux, execute
```bash
python3.9 -m venv TDDash
```

### Ative o ambiente de desenvolvimento virtual

- No ambiente Windows, no bash do git, execute
```bash
source TDDash/Scripts/activate
```

- No ambiente Linux, execute
```bash
source TDDash/bin/activate
```

### Instale as dependências desse repositório

```bash
pip install -r requirements.txt
```

### Instale as dependências do repositório pyDash clonado

```bash
pip install -r pydash/requirements.txt
```

## Como usar

### Copie o algoritmo ABR implementado

Primeiro, copie arquivo **r2a_finetunedcontrol.py** da pasta r2a desse repositório e cole na pasta pydash/r2a. Depois, modifique o valor da chave "r2a_algorithm" do arquivo pydash/dash_client.json para **R2A_FineTunedControl**.

### Avalie o código

Para avaliar o código, ative o ambiente de desenvolvimento, mude para a pasta pydash com o comando

``` bash
cd pydash/
```

e execute o comando

``` bash
python main.py
```

## Resultados

Aqui estão alguns dos resultados obtidos com o algoritmo implementado.
