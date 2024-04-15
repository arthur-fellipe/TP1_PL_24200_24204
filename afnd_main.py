import json
import argparse
import sys

# Variável global para contagem de estados
counter = 0

# Definindo funções para cada operação
def alt(args):
    global counter
    
    # Criar estados e transições para o primeiro autômato/símbolo
    afnd1 = args[0]
    
    # Criar estados e transições para o segundo autômato/símbolo
    afnd2 = args[1]
    
    # Cria um novo estado inicial para o AFND resultante
    novo_estado_inicial = f'q{counter}'
    counter += 1

    # Define as transições vazias do novo estado inicial para os estados iniciais de afnd1 e afnd2
    novo_delta = {"": [afnd1["q0"], afnd2["q0"]]}

    # Atualiza o conjunto de estados, alfabeto e conjunto de estados finais do AFND resultante
    novo_afnd = {
        "Q": [novo_estado_inicial] + afnd1["Q"] + afnd2["Q"],
        "Sigma": afnd1["Sigma"] | afnd2["Sigma"],
        "delta": {**novo_delta, **afnd1["delta"], **afnd2["delta"]},
        "q0": novo_estado_inicial,
        "F": afnd1["F"] + afnd2["F"]
    }

    return novo_afnd
# def alt(args):
#     global counter
    
#     # Criar estados e transições para o primeiro autômato/símbolo
#     afnd1 = args[0]
    
#     # Criar estados e transições para o segundo autômato/símbolo
#     afnd2 = args[1]
    
#     novo_estado_1 = f'q{counter}'
#     counter += 1
#     novo_estado_2 = f'q{counter}'
#     counter += 1
    
#     # Atualizar estados finais e transições do primeiro autômato/símbolo
#     for estado in afnd1['F']:
#         afnd1['delta'][estado]['ε'] = [novo_estado_1]
#     afnd1['F'] = [novo_estado_1]
    
#     # Atualizar estados finais e transições do segundo autômato/símbolo
#     for estado in afnd2['F']:
#         afnd2['delta'][estado]['ε'] = [novo_estado_2]
#     afnd2['F'] = [novo_estado_2]
    
#     # Unir os dois autômatos em um novo autômato
#     delta = {}
#     delta.update(afnd1['delta'])
#     delta.update(afnd2['delta'])
    
#     # Atualizar estado inicial e estados finais
#     q0 = 'q0'
#     F = afnd1['F'] + afnd2['F']
    
#     return {
#         "Q": "",
#         "V": "",
#         "q0": q0,
#         "F": F,
#         "delta": delta
#     }

def seq(args):
    afnd1 = args[0]
    afnd2 = args[1]

    if not isinstance(afnd1['F'], list):
        raise Exception("afnd1['F'] deve ser uma lista")
    if not isinstance(afnd2['delta'], dict):
        raise Exception("afnd2['delta'] deve ser um dicionário")

    # Atualizar transições para ligar os estados finais de afnd1 ao estado inicial de afnd2
    for estado in afnd1['F']:
        if estado in afnd2['delta']:
            if not isinstance(afnd1['delta'].get(estado, {}), dict):
                raise Exception("afnd1['delta'][estado] deve ser um dicionário")
            if 'ε' in afnd1['delta'][estado]:
                if not isinstance(afnd1['delta'][estado]['ε'], list):
                    raise Exception("afnd1['delta'][estado]['ε'] deve ser uma lista")
                afnd1['delta'][estado]['ε'].append(afnd2['q0'])
            else:
                afnd1['delta'][estado]['ε'] = [afnd2['q0']]
    
    # Atualizar estados finais e transições
    afnd1['F'] = afnd2['F']
    afnd1['delta'].update(afnd2['delta'])

    # Retornar o autômato resultante
    return afnd1

def kle(args):
    global counter
    
    afnd = args[0]
    
    novo_estado_1 = f'q{counter}'
    counter += 1
    novo_estado_2 = f'q{counter}'
    counter += 1

    # Atualizar transições para o fecho de Kleene
    afnd['delta'][afnd['q0']]['ε'] = [novo_estado_1, novo_estado_2]
    
    # Adicionar transições para o novo estado final
    afnd['delta'][novo_estado_1] = {'ε': [afnd['q0']]}
    afnd['delta'][novo_estado_2] = {'ε': [novo_estado_1, afnd['F'][0]]}

    # Atualizar estados finais e transições
    afnd['F'] = [novo_estado_2]

    # Retornar o autômato resultante
    return {
        "Q": "",
        "V": "",
        "q0": afnd['q0'],
        "F": afnd['F'],
        "delta": afnd['delta']
    }

def trans(args):
    global counter
    
    simbolo = args[0][0] if isinstance(args[0], tuple) else args[0]
    
    novo_estado = f'q{counter}'
    counter += 1

    # Criar transição
    transicoes = {simbolo: novo_estado}

    # Retornar o autômato resultante
    return {
        "Q": "",
        "V": "",
        "q0": 'q0',
        "F": [novo_estado],
        "delta": {'q0': transicoes}
    }

# Dicionário de operadores e suas prioridades
operadores : dict = {
    'alt': (alt, 0),
    'seq': (seq, 1),
    'kle': (kle, 2),
    'trans': (trans, 3)
}

# Avaliação da árvore de expressão regular
def evaluate(arv):
    global counter
    
    if isinstance(arv, dict):
        print(f"Entrou em evaluate com árvore: {arv}")  # Debug: Mostra a árvore que estamos avaliando
        
        if 'op' in arv:
            print(f"Operação: {arv['op']}")  # Debug: Mostra a operação
            
            args_res = [evaluate(a) for a in arv['args']]
            print(f"Resultados dos argumentos: {args_res}")  # Debug: Mostra os resultados dos argumentos
            
            return operadores[arv['op']](*args_res)
        
        elif 'simb' in arv:
            print(f"Símbolo: {arv['simb']}")  # Debug: Mostra o símbolo que estamos avaliando
            
            # Cria dois novos estados para representar a transição com o símbolo
            estado_inicial = f'q{counter}'
            counter += 1
            estado_final = f'q{counter}'
            counter += 1

            # Define a transição com o símbolo do estado inicial para o estado final
            delta = {estado_inicial: {arv["simb"]: [estado_final]}}
            
            return {
                "Q": [estado_inicial, estado_final],
                "Sigma": {arv["simb"]},
                "delta": delta,
                "q0": estado_inicial,
                "F": [estado_final]
            }
        
        elif 'epsilon' in arv:
            print("Epsilon")  # Debug: Mostra que encontramos um epsilon
            
            # Cria um novo estado inicial e final para representar a transição com epsilon
            estado_inicial = f'q{counter}'
            counter += 1
            estado_final = f'q{counter}'
            counter += 1
            
            # Define a transição com epsilon do estado inicial para o estado final
            delta = {estado_inicial: {'ε': [estado_final]}}
            
            return {
                "Q": [estado_inicial, estado_final],
                "Sigma": "ε",
                "delta": delta,
                "q0": estado_inicial,
                "F": [estado_final]
            }
            
    raise Exception("Formato de árvore de expressão regular inválido")

def main():
    input_file = "er01.json"  # Nome do arquivo de entrada
    output_file = "afnd.json"  # Nome do arquivo de saída
    
    with open(input_file, 'r') as f:
        try:
            arvore = json.load(f)
            print(f"Arvore após carregamento: {arvore}")
            afnd = evaluate(arvore)
            print(f"AFND resultante: {afnd}")

            with open(output_file, 'w') as out_file:
                json.dump(afnd, out_file, indent=4)
            
            print(f"Autômato salvo em {output_file}")
        except Exception as e:
            print(f"Erro: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

# # Função principal
# def main():
#     parser = argparse.ArgumentParser(description='Processa um arquivo de expressão regular e um arquivo de saída.')
#     parser.add_argument('er_file', help='O arquivo de expressão regular a ser processado.')
#     parser.add_argument('--output', required=True, help='O arquivo de saída onde os resultados serão gravados.')
#     args = parser.parse_args()

#     with open(args.er_file, 'r') as f:
#         try:
#             arvore = json.load(f)
#             print(f"Arvore após carregamento: {arvore}")
#             afnd = evaluate(arvore)
#             print(f"AFND resultante: {afnd}")

#             with open(args.output, 'w') as output_file:
#                 json.dump(afnd, output_file, indent=4)
            
#             print(f"Autômato salvo em {args.output}")
#         except Exception as e:
#             print(f"Erro: {e}", file=sys.stderr)

# if __name__ == "__main__":
#     main()



# # Variável global para contagem de estados
# counter = 0

# # Definindo funções para cada operação
# def alt(args):
#     global counter
#     arg1 = args[0] if isinstance(args[0], dict) else args[0][0]
#     arg2 = args[1] if isinstance(args[1], dict) else args[1][0]

#     novo_estado_1 = f'q{counter}'
#     counter += 1
#     novo_estado_2 = f'q{counter}'
#     counter += 1

#     transicoes_1 = {arg1: novo_estado_1}
#     transicoes_2 = {arg2: novo_estado_2}
#     transicoes_epsilon = {'ε': [novo_estado_1, novo_estado_2]}

#     return {'q0': 'q1', 'F': ['qf'], 'delta': {'q0': transicoes_epsilon, novo_estado_1: transicoes_1, novo_estado_2: transicoes_2}}

# def seq(args):
#     afnd1 = args[0] if isinstance(args[0], dict) else args[0][0]
#     afnd2 = args[1] if isinstance(args[1], dict) else args[1][0]

#     for estado in afnd1['F']:
#         if estado in afnd2['delta']:
#             afnd1['F'].remove(estado)
#             afnd1['delta'][estado]['ε'] = afnd1['delta'][estado].get('ε', []) + [afnd2['q0']]

#     afnd1['F'] = afnd2['F']
#     afnd1['delta'].update(afnd2['delta'])

#     return afnd1

# def kle(args):
#     afnd = args[0] if isinstance(args[0], dict) else args[0][0]
#     afnd['delta']['q0']['ε'] = afnd['delta']['q0'].get('ε', []) + ['qf']
#     afnd['delta']['qf'] = {'ε': ['q0']}
#     afnd['F'] = ['qf']

#     return afnd

# def trans(args):
#     global counter
#     arg = args[0] if isinstance(args[0], str) else args[0][0]
#     simbolo = arg[0] if isinstance(arg, tuple) else arg
#     novo_estado = f'q{counter}'
#     counter += 1

#     transicoes = {simbolo: novo_estado}

#     return {'q0': 'q1', 'F': [novo_estado], 'delta': {'q0': transicoes}}

# # Dicionário de operadores e suas prioridades
# operadores : dict = {
#     'alt': (alt, 0),
#     'seq': (seq, 1),
#     'kle': (kle, 2),
#     'trans': (trans, 3)
# }

# # Avaliação da árvore de expressão regular
# def evaluate(arv):
#     if isinstance(arv, dict):
#         if 'op' in arv:
#             op, op_priority = operadores[arv['op']]
#             args_res = [evaluate(a) for a in arv['args']]
#             # Processa os argumentos com base na prioridade
#             processed_args = [a[0] if op_priority < a[1] else f'({a[0]})' for a in args_res]
#             return op(processed_args), op_priority

#         elif 'simb' in arv:
#             return arv['simb'], 3

#         elif 'epsilon' in arv:
#             return 'ε', 3

#             # processed_args = []
#             # for a in arv['args']:
#             #     arg = evaluate(a) if isinstance(a, dict) else a
#             #     if isinstance(arg, tuple):
#             #         processed_arg = arg if op_priority < arg[1] else f'({arg[0]})'
#             #     else:
#             #         processed_arg = arg
#             #     processed_args.append(processed_arg)
            
#             # return op(processed_args), op_priority

#         # elif 'simb' in arv:
#         #     return arv['simb']

#         # elif 'epsilon' in arv:
#         #     return 'ε'

#     raise Exception("Formato de árvore de expressão regular inválido")


# # Função principal
# def main():
#     parser = argparse.ArgumentParser(description='Processa um arquivo de expressão regular e um arquivo de saída.')
#     parser.add_argument('er_file', help='O arquivo de expressão regular a ser processado.')
#     # parser.add_argument('--output', required=True, help='O arquivo de saída onde os resultados serão gravados.')
#     args = parser.parse_args()

#     with open(args.er_file, 'r') as f:
#         try:
#             arvore = json.load(f)
#             print("Arvore após carregamento:", arvore)
#             afnd, _ = evaluate(arvore)
#             print(afnd)
#             # with open(args.output, 'w') as output_file:
#             #     json.dump(afnd, output_file, indent=4)
#         except Exception as e:
#             print(e, file=sys.stderr)

# if __name__ == "__main__":
#     main()
 

"""
def construir_arvore(er):
    if isinstance(er, str):
        return {"op": "simb", "args": er}
    elif "simb" in er:
        return {"op": "simb", "args": er["simb"]}
    elif "epsilon" in er:
        return {"op": "epsilon", "args": None}
    elif "plus" in er:
        return {"op": "plus", "args": [construir_arvore(arg) for arg in er["args"]]}
    else:
        op = er["op"]
        args = [construir_arvore(arg) for arg in er["args"]]
        return {"op": op, "args": args}

def converter_para_afnd(arvore):
    if arvore["op"] == "simb":
        q0 = "q0"
        F = ["qf"]
        delta = {"q0": {arvore["args"]: "qf"}}
        return {"q0": q0, "F": F, "delta": delta}
    elif arvore["op"] == "epsilon":
        q0 = "q0"
        F = ["qf"]
        delta = {"q0": {"ε": "qf"}}
        return {"q0": q0, "F": F, "delta": delta}
    elif arvore["op"] == "alt":
        afnd1 = converter_para_afnd(arvore["args"][0])
        afnd2 = converter_para_afnd(arvore["args"][1])
        
        q0 = "q0"
        F = ["qf"]
        
        delta = {"q0": {"ε": [afnd1["q0"], afnd2["q0"]]},
                 afnd1["F"][0]: {"ε": "qf"},
                 afnd2["F"][0]: {"ε": "qf"}}
        
        delta.update(afnd1["delta"])
        delta.update(afnd2["delta"])
        
        return {"q0": q0, "F": F, "delta": delta}
    elif arvore["op"] == "seq":
        afnd1 = converter_para_afnd(arvore["args"][0])
        afnd2 = converter_para_afnd(arvore["args"][1])
        
        q0 = afnd1["q0"]
        F = afnd2["F"]
        
        delta = afnd1["delta"]
        delta.update(afnd2["delta"])
        
        for f in afnd1["F"]:
            if "ε" in delta[f]:
                delta[f]["ε"].append(afnd2["q0"])
            else:
                delta[f]["ε"] = [afnd2["q0"]]
        
        return {"q0": q0, "F": F, "delta": delta}
    elif arvore["op"] == "kle":
        afnd = converter_para_afnd(arvore["args"][0])
        
        q0 = "q0"
        F = ["qf"]
        
        delta = {"q0": {"ε": [afnd["q0"], "qf"]},
                 afnd["F"][0]: {"ε": [afnd["q0"], "qf"]}}
        
        delta.update(afnd["delta"])
        
        return {"q0": q0, "F": F, "delta": delta}
    elif arvore["op"] == "plus":
        afnd = converter_para_afnd(arvore["args"][0])
        
        q0 = afnd["q0"]
        F = afnd["F"]
        
        delta = afnd["delta"]
        
        for f in afnd["F"]:
            if "ε" in delta[f]:
                delta[f]["ε"].append(afnd["q0"])
            else:
                delta[f]["ε"] = [afnd["q0"]]
        
        return {"q0": q0, "F": F, "delta": delta}


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
"""
