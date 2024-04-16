import json
import argparse

contador_estados : int = 1

def novo_estado():
    global contador_estados
    estado = f"q{contador_estados}"
    contador_estados += 1
    return estado

def construir_arvore(er):
    if isinstance(er, str):
        return {"op": "simb", "args": er}
    elif "simb" in er:
        return {"op": "simb", "args": er["simb"]}
    elif "ε" in er:
        return {"op": "ε", "args": None}
    elif "plus" in er:
        return {"op": "plus", "args": [construir_arvore(arg) for arg in er["args"]]}
    else:
        op = er["op"]
        args = [construir_arvore(arg) for arg in er["args"]]
        return {"op": op, "args": args}

def converter_para_afnd(arvore):
    estados = set()
    transicoes = {}

    def adicionar_transicao(origem, simbolo, destino):
        if origem not in transicoes:
            transicoes[origem] = {}
        transicoes[origem][simbolo] = destino

    def percorrer_arvore(no, estado_inicial, estado_final):
        if no["op"] == "simb":
            estado_atual = novo_estado()
            estados.add(estado_atual)
            adicionar_transicao(estado_inicial, no["args"], estado_atual)
            adicionar_transicao(estado_atual, "ε", estado_final)
        elif no["op"] == "ε":
            adicionar_transicao(estado_inicial, "ε", estado_final)
        elif no["op"] == "plus":
            estado_atual = novo_estado()
            estados.add(estado_atual)
            adicionar_transicao(estado_inicial, "ε", estado_atual)
            for arg in no["args"]:
                percorrer_arvore(arg, estado_atual, estado_final)
        else:
            estado_atual = novo_estado()
            estados.add(estado_atual)
            for arg in no["args"]:
                percorrer_arvore(arg, estado_inicial, estado_atual)
            adicionar_transicao(estado_atual, "ε", estado_final)

    estado_inicial = novo_estado()
    estado_final = novo_estado()
    estados.add(estado_inicial)
    estados.add(estado_final)
    percorrer_arvore(arvore, estado_inicial, estado_final)

    # Extrair os símbolos do alfabeto (V) do dicionário de transições
    alfabeto = set()
    for origem, trans in transicoes.items():
        for simbolo in trans.keys():
            alfabeto.add(simbolo)

    afnd = {
        "Q": list(estados),  # Estados
        "V": list(alfabeto),  # Alfabeto
        "q0": estado_inicial,  # Estado inicial
        "F": [estado_final],  # Estados finais
        "delta": transicoes  # Transições
    }

    return afnd

def ler_er(nome_arquivo):
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        er = json.load(f)
        if isinstance(er, str):
            raise ValueError("O arquivo JSON deve representar um objeto, não uma string.")
        return er

def main():
    parser = argparse.ArgumentParser(description='Conversor de Expressão Regular para AFND')
    parser.add_argument('ficheiro', type=str, help='Ficheiro JSON da expressão regular')
    parser.add_argument('--output', type=str, help='Ficheiro JSON de saída para o AFND')

    args = parser.parse_args()

    er = ler_er(args.ficheiro)

    arvore = construir_arvore(er)
    afnd = converter_para_afnd(arvore)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(afnd, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()