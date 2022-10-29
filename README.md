# TD-2021-2_ABR-algorithm

![](https://img.shields.io/badge/version-v0.1-blue)

Este repositório corresponde ao projeto final de programação da disciplina de Transmissão de Dados da Universidade de Brasília e implementa uma versão adaptada do algoritmo ABR desenvolvido por *Ito et al.* publicado como

> M. S. Ito, D. Bezerra, S. Fernandes, D. Sadok and G. Szabo, ["A fine-tuned control-theoretic approach for dynamic adaptive streaming over HTTP"](https://ieeexplore.ieee.org/document/7405532), 2015 IEEE Symposium on Computers and Communication (ISCC), 2015, pp. 301-308, doi: 10.1109/ISCC.2015.7405532.

Além disso, para simulação do algoritmo, foi utilizado a plataforma PyDash desenvolvida por *Marotta et al.* disponível neste [respositório](https://github.com/mfcaetano/pydash.git) e publicada como

> M. A. Marotta, G. C. Souza, M. Holanda and M. F. Caetano, ["PyDash - A Framework Based Educational Tool for Adaptive Streaming Video Algorithms Study"](https://ieeexplore.ieee.org/document/9637335), 2021 IEEE Frontiers in Education Conference (FIE), 2021, pp. 1-8, doi: 10.1109/FIE49875.2021.9637335.

## Configurações

- Versão do Python: 3.9.5

Para definir as configurações do projeto, instale a versão do Python utilizada e o instalador de pacotes pip. Depois, siga as etapas para criação e ativação do ambiente de desenvolvimento de acordo com o seu sistema operacional na pasta **root** desse repositório.

### Clone o repositório PyDash utilizado

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

### Instale as dependências do repositório PyDash clonado

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