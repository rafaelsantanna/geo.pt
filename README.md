# Script de Dados Administrativos de Portugal

## O que este script faz?

O script é como um **robô que busca informações** sobre todas as cidades e bairros de Portugal na internet. Ele funciona em 4 etapas simples:

### 1. Buscar Dados na Internet
O script vai até o site oficial do governo português (dados.gov.pt) e baixa duas planilhas:
- Uma com todos os **concelhos** (como se fossem municípios/cidades)
- Outra com todas as **freguesias** (como se fossem bairros/distritos locais)

### 2. Organizar as Informações
Depois de baixar, ele organiza tudo em 3 categorias:
- **20 Distritos** - As grandes regiões de Portugal (como estados)
- **308 Concelhos** - As cidades dentro de cada distrito
- **3091+ Freguesias** - Os bairros dentro de cada cidade

Cada lugar recebe um código único (tipo um CEP) chamado DICOFRE.

### 3. Salvar em Arquivos
O script cria 4 arquivos na pasta "portugal_dados":
- **distritos.csv** - Lista dos 20 distritos
- **concelhos.csv** - Lista das 308 cidades
- **freguesias.csv** - Lista dos 3091+ bairros
- **portugal_completo.json** - Tudo junto num único arquivo

### 4. Criar um Relatório
No final, mostra um resumo com:
- Quantos lugares foram encontrados
- Se está tudo completo
- Estatísticas gerais

## Como executar o script

### Requisitos
- Python 3.6 ou superior
- Conexão com a internet

### Instalação
O script instala automaticamente as bibliotecas necessárias (pandas e openpyxl) se não estiverem instaladas.

### Executar
Abra o terminal/prompt de comando na pasta do script e execute:

```bash
python portugal_geo_fetch.py
```

Ou se tiver Python 3:

```bash
python3 portugal_geo_fetch.py
```

### Resultado
Após executar, você terá uma pasta `portugal_dados/` com todos os arquivos:
- `distritos.csv`
- `concelhos.csv`
- `freguesias.csv`
- `portugal_completo.json`

## Para que serve?

Este script é útil para:
- Sistemas que precisam de listas de cidades e bairros de Portugal
- Formulários com seleção de localização
- Aplicações de entrega ou logística
- Análises geográficas
- Qualquer sistema que precise da divisão administrativa de Portugal

**Em resumo:** É como se fosse um assistente que automaticamente baixa, organiza e salva toda a divisão administrativa de Portugal - desde as grandes regiões até os pequenos bairros - tudo pronto para usar em outros sistemas ou aplicações.