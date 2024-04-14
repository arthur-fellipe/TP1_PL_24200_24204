import json
import argparse
from graphviz import Digraph

# automato : dict = {}
 
# Lê a definição do autômato a partir de um arquivo JSON e retorna a definição como um dicionário.
def ler_automato(nome_arquivo):
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        return json.load(f)

def gerar_diagrama(automato):
    # Gerar o diagrama de grafos do automato
    dot = Digraph(comment='Automato')
    
    # 'none' para um node invisível
    dot.node('start', shape='none', label='')
    # criar transição incial
    dot.edge('start', automato["q0"], label='')

    # Criar os estados
    for estado in automato["F"]:
        # caso o estado seja final
        if estado in automato["F"]:
            dot.node(estado, estado, shape="doublecircle")
        else:
            dot.node(estado, estado, shape="circle")

    # Criar as transições
    for estado_inicial, transitions in automato["delta"].items():
        for simbolo, estado_final in transitions.items():
            dot.edge(estado_inicial, estado_final, label = simbolo)

    return dot

def reconhecedor(entrada, estado_inicial, transicoes, estados_finais):
    entrada = entrada.replace("ε", "")

    estado_atual = estado_inicial
    caminho = [estado_atual]

    for char in entrada:
        # caso haja uma transição
        if char in transicoes[estado_atual]:
            estado_atual = transicoes[estado_atual][char]
            caminho.append((estado_atual))

        # caso haja uma transição com a palavra vazia
        elif "ε" in transicoes[estado_atual]:
            estado_atual_aux = transicoes[estado_atual]["ε"]
            if char in transicoes[estado_atual_aux]:
                estado_atual = transicoes[estado_atual_aux][char]
                caminho.append((estado_atual))
            else:
                # se não houver transição definida para este caracter de entrada, a palavra não é aceite
                return False, caminho, f"símbolo '{char}' não pertence ao alfabeto"
        else:
            return False, caminho, f"símbolo '{char}' não pertence ao alfabeto"

    if estado_atual in estados_finais:
        return True, caminho, f"estado {estado_atual} é final"
    else:
        return False, caminho, f"estado {estado_atual} não é final"

def main():
    parser = argparse.ArgumentParser(description='Automato Finito Determinista')
    parser.add_argument('ficheiro', type=str, help='Ficheiro JSON do automato')
    parser.add_argument('-graphviz', action='store_true', help='Gerar diagrama do automato')
    parser.add_argument('-reconhecer', type=str, help='Reconhecer palavra')

    args = parser.parse_args()

    automato = ler_automato(args.ficheiro)

    if args.graphviz:
        dot = gerar_diagrama(automato)
        dot.render('automaton_graph', view=True, format='png')

    if args.reconhecer:
        palavra = args.reconhecer
        resultado, caminho, mensagem = reconhecedor(palavra, automato["estado_inicial"], automato["transicoes"], automato["estados_finais"])
        if resultado:
            print(f"A palavra '{palavra}' é aceite pelo automato.")
            print(f"Caminho: {caminho}")
        else:
            print(f"A palavra '{palavra}' não é aceite pelo automato.")
            print(f"Erro: {mensagem}")

if __name__ == "__main__":
    main()