import json
import argparse

# Função que converte um AFND em um AFD
def converter_afnd_para_afd(afnd: dict) -> dict:

    # Função para encontrar o conjunto de estados alcançáveis a partir de um estado e um símbolo
    def encontrar_alcancaveis(estado_atual, simbolo, transicoes):
        alcancaveis = set()
        for estado in estado_atual:
            if estado in transicoes and simbolo in transicoes[estado]:
                alcancaveis.update(transicoes[estado][simbolo])
        return frozenset(alcancaveis)

    # Função para calcular o fecho-ε de um conjunto de estados
    def fecho_epsilon(conjunto, transicoes):
        fecho = set(conjunto)

        def aumentar_fecho(estado):
            if estado in transicoes and 'ε' in transicoes[estado]: 
                for proximo_estado in transicoes[estado]['ε']:
                    if proximo_estado not in fecho:
                        fecho.add(proximo_estado)
                        aumentar_fecho(proximo_estado)

        for estado in conjunto:
            aumentar_fecho(estado) 

        return frozenset(fecho)

    # Função para construir o AFD
    def construir_afd(estados_atuais):
        nonlocal estados_afd, pilha, transicoes_afd
        for simbolo in alfabeto_afd:
            alcancaveis = encontrar_alcancaveis(estados_atuais, simbolo, transicoes_afnd)
            fecho_epsilon_alcancaveis = fecho_epsilon(alcancaveis, transicoes_afnd)
            if fecho_epsilon_alcancaveis:
                if fecho_epsilon_alcancaveis not in estados_afd.values():
                    estados_afd[f"N{len(estados_afd)}"] = fecho_epsilon_alcancaveis
                    pilha.append(fecho_epsilon_alcancaveis)
                for estado, valor in estados_afd.items():
                    if valor == estados_atuais:
                        estado_atual = estado 
                    if valor == fecho_epsilon_alcancaveis: 
                        proximo_estado = estado
                transicoes_afd.setdefault(estado_atual, {})[simbolo] = proximo_estado

        if pilha:
            construir_afd(pilha.pop())

    transicoes_afnd = afnd['delta']
    estado_inicial_afnd = afnd['q0']
    estados_finais_afnd = set(afnd['F'])
    estados_afd = {}
    alfabeto_afd = [simbolo for simbolo in afnd['V'] if simbolo != 'ε']
    transicoes_afd = {}
    pilha = []

    # Inicializa o AFD com o fecho-ε do estado inicial do AFND
    fecho_inicial = fecho_epsilon({estado_inicial_afnd}, transicoes_afnd)
    estados_afd[f"N{len(estados_afd)}"] = fecho_inicial
    pilha.append(fecho_inicial)

    construir_afd(pilha.pop())

    estados_finais_afd = []
    for estado, fecho in estados_afd.items():
        if fecho.intersection(estados_finais_afnd):
            estados_finais_afd.append(estado)

    afd = {
        "Q": list(estados_afd.keys()),
        "V": alfabeto_afd,
        "q0": "N0",
        "F": estados_finais_afd,
        "delta": transicoes_afd
    }
    return afd

# Função para carregar um autômato de um arquivo JSON
def carregar_automato(json_file: str) -> dict:
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)

# Função para salvar um autômato em um arquivo JSON
def salvar_automato(afd, json_file: str) -> None:
    with open(json_file, 'w' , encoding='utf-8') as file:
        json.dump(afd, file, ensure_ascii=False, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Conversão de AFND para AFD")
    parser.add_argument("arquivo_json", 
                        help="Caminho para o arquivo JSON contendo a definição do AFND")
    parser.add_argument('-output', metavar='output_file', type=str,
                        help='Arquivo JSON de saída para o AFD')

    args = parser.parse_args()

    afnd = carregar_automato(args.arquivo_json)
    afd = converter_afnd_para_afd(afnd)
    salvar_automato(afd, args.output)

if __name__ == "__main__":
    main()
