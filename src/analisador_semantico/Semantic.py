import sys
from Token import Token  # Importando classe de tokens
from tabela_simbolos.SymbolTables import SymbolTable, FunctionSymbolTable
from tabela_simbolos.Variable import Variable


class Semantic:
    def __init__(self, tokens):
        # ====================
        # TABELA DE SIMBOLOS - VARIAVEIS
        self.__tipo = None                     # Tipo da variavel a ser armazenada
        self.__varName = None                  # Nome da variavel a ser armazenada
        self.__symbolTable = SymbolTable()     # Classe Tabela de simbolos - Variaveis
        self.__symbol = None                   # Classe Variable

        # ====================
        # TABELA DE SIMBOLOS - FUNÇÃO
        self.__escopo = None                    # Indicação de escopo para inserção na tabela
        self.__retorno_func = None              # Retorno da funcao
        self.__num_parametros = 0               # Numero de parametros da funcao
        self.__functionSymbolTable = FunctionSymbolTable()  # Classe Tabela de simbolos - Funcao
        self.__name_scope = None    # Nome do escopo na atribuicao de funcao

        # ====================
        # VARIAVEIS AUXILIARES - COMPATIBILIDADE DE TIPOS
        self.__varTypeAssign = None          # Armazena o tipo da variavel da atribuicao
        self.__assignmentTypeError = None    # Armazena o tipo da variavel que foi atribuido errado
        self.__type_op_logic01 = ''          # Tipo do primeiro operador logico
        self.__type_op_logic02 = ''          # Tipo do segundo operador logico
        self.__op_logic_conditional = False          # Flag que não é uma atribuição lógica

        # ====================================== 
        # VARIAVEIS - SINTATICA      
        self._table_tokens = tokens  # Lista com todos os tokens [('BAHTCHE', 'TK_MAIN', 1, 1), ...]
        self._error = 'no error'  # Flag de erro
        self._count = 0  # Indica qual o token da lista está sendo lido
        self._token = self._proximo_tk()  # Variavel que indica o token atual que está sendo lido

        self._tipos = [
            Token.TK_INT,
            Token.TK_STRING,
            Token.TK_FLOAT
        ]

        self._operadores_matematicos = [
            Token.TK_MATH_ADD,
            Token.TK_MATH_SUB,
            Token.TK_MATH_MUL,
            Token.TK_MATH_DIV
        ]

        self._operadores_logicos = [
            Token.TK_LOGIC_AND,  # &&
            Token.TK_LOGIC_OR,  # ||
            Token.TK_LOGIC_DIF,  # !=
            Token.TK_LOGIC_LG,  # <,>
            Token.TK_LOGIC_LE_GE,  # <=, >=
            Token.TK_LOGIC_EQ  # ==
        ]

        self._conjunto_operandos = [
            Token.TK_IDENT,
            Token.TK_NUMBER,
            Token.TK_REAL
        ]

        self._conjunto_tokens_content = [
            Token.TK_IDENT,
            Token.TK_WHILE,
            Token.TK_IF,
            Token.TK_SCANF,
            Token.TK_PRINT,
            Token.TK_CK,
            Token.TK_RETURN
        ] + self._tipos

    # ====================
    # DEFINE A MENSAGEM DE ERRO SEMANTICO
    def _mensagem(self, current_symbol=None, line=None, column=None):
        if self._error == 'already_declared_variable':
            return f'\t [Erro Semantico] | Mas BAH, a variavel {self.__varName} ja foi declarada | line: {line} column: {column}'
        elif self._error == 'undeclared_variable':
            return f'\t [Erro Semantico] | Mas BAH, variavel {current_symbol} nao foi declarada | line: {line} column: {column}'
        elif self._error == 'already_declared_function':
            return f'\t [Erro Semantico] | Mas BAH, a funcao {self.__escopo} ja foi declarada | line: {line} column: {column}'
        elif self._error == 'tipo_retorno_invalido':
            return f'\t [Erro Semantico] | Mas BAH, {current_symbol} nao eh um tipo de retorno valido para a funcao {self.__escopo} | line: {line} column: {column}'
        elif self._error == 'undeclared_function':
            return f'\t [Erro Semantico] | Mas BAH, a funcao {current_symbol} nao foi declarada | line: {line} column: {column}'
        elif self._error == 'error_num_param':
            return f'\t [Erro Semantico] | Mas BAH, quantidade de parametros incorreta na chamada da funcao {self.__name_scope} | line: {line} column: {column}'
        elif self._error == 'division_by_zero':
            return f'\t [Erro Semantico] | Mas BAH, divisao por 0 | line: {line} column: {column}'
        elif self._error == 'logic_error':
            return f'\t [Erro Semantico] | Mas BAH, operacao logica entre tipos incompativeis | line: {line} column: {column}'
        elif self._error == 'type_incompatible':
            return f'\t [Erro Semantico] | Mas BAH, esperado tipo {self._typeAsTheToken(self.__varTypeAssign)} em vez de {self._typeAsTheToken(self.__assignmentTypeError)} | line: {line} column: {column}'

    # ====================
    # RETORNA O TIPO CONFORME O TOKEN
    def _typeAsTheToken(self, text):
        if text == 'TK_NUMBER' or (text == 'TK_INT'):
            return 'GURI'
        elif (text == 'TK_FLOAT') or (text == 'TK_REAL'):
            return 'GURIZAO'
        elif (text == 'TK_STRING') or (text == 'TK_TEXT'):
            return 'FANDANGO'

    # ====================
    # VERIFICA A CORRESPONDENCIA DO TOKEN LIDO COM O ESPERADO
    def _terminal(self, token=None):
        # Token atual lido
        current_token = self._token  # ('BAHTCHE', 'TK_MAIN', 1, 1)

        # Caso terminou de ler a lista de tokens, mas a gramatica não finalizou
        if current_token == 'finish':
            self._error = 'finish'
            raise Exception(self._mensagem())

        # Caso tenha sido lancado na flag self._error algum erro
        if self._error != 'no error':
            raise Exception(self._mensagem(current_token[0], current_token[2], current_token[3]))

        # Lanca erro - Verificando se o token atual não corresponde ao token lido
        if not (current_token[1] in token):
            raise Exception(self._mensagem(current_token[0], current_token[2], current_token[3]))

        # Caso não haja erro de terminal - Proximo token
        self._token = self._proximo_tk()

    #####################################################
    ############### REGRAS SEMANTICAS ###################
    #####################################################

    def _if(self):
        self._terminal([Token.TK_IF])

    def _elif(self):
        self._terminal([Token.TK_ELIF])

    def _else(self):
        self._terminal([Token.TK_ELSE])

    def _declara_elif(self):
        if self._token[1] == Token.TK_ELIF:

            self._elif()
            self._open_p()

            if self._token[1] != Token.TK_CP:
                # Ativa a flag como True para indicar operacao logica no contexto de condicional
                self.__op_logic_conditional = True

                self._op_logic()
            else:
                self._error = 'expressao_vazia'
                self._terminal()

            # Verificacao de compatibilidade de tipos da operacao
            if self.__type_op_logic01 != self.__type_op_logic02:
                self._error = 'logic_error'
                self._terminal()

            self._close_p()

            # Desaativa a flag
            self.__op_logic_conditional = False

            self._openKey()
            self._content()
            self._closeKey()
            self._declara_elif()

    def _declara_else(self):
        if self._token[1] == Token.TK_ELSE:
            self._else()
            self._openKey()
            self._content()
            self._closeKey()

    def _condicional(self):
        self._if()
        self._open_p()

        if self._token[1] != Token.TK_CP:
            # Ativa a flag como True para indicar operacao logica no contexto de condicional
            self.__op_logic_conditional = True

            self._op_logic()
        else:
            self._error = 'expressao_vazia'
            self._terminal()

        # Verificacao de compatibilidade de tipos da operacao
        if self.__type_op_logic01 != self.__type_op_logic02:
            self._error = 'logic_error'
            self._terminal()

        self._close_p()

        # Desaativa a flag
        self.__op_logic_conditional = False

        self._openKey()
        self._content()
        self._closeKey()
        self._declara_elif()
        self._declara_else()

    def _term(self):
        if self._token[1] == Token.TK_IDENT:
            # Verifica se a variavel foi declarada
            if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
                self._error = 'undeclared_variable'
                self._terminal()

            # Verifica compatibilidade de tipos
            tipo = self.__symbolTable.returnsTypeVariable(escopo=self.__escopo, identificador=self._token[0])

            if not self.__symbolTable.typeComparison(tipo, self.__varTypeAssign):
                self.__assignmentTypeError = tipo
                self._error = 'type_incompatible'
                self._terminal()

            self._identificador()
        elif self._token[1] == Token.TK_NUMBER:
            # Verifica compatibilidade de tipos
            if not self.__symbolTable.typeComparison(Token.TK_INT, self.__varTypeAssign):
                self.__assignmentTypeError = self._token[1]
                self._error = 'type_incompatible'
                self._terminal()

            self._number()
        elif self._token[1] == Token.TK_REAL:
            # Verifica compatibilidade de tipos
            if not self.__symbolTable.typeComparison(Token.TK_FLOAT, self.__varTypeAssign):
                self.__assignmentTypeError = self._token[1]
                self._error = 'type_incompatible'
                self._terminal()

            self._real()
        else:
            self._error = 'operacao_matematica_invalida'
            self._terminal()

    def _mul_div_add_sub(self):
        if self._token[1] == Token.TK_MATH_MUL:
            self._terminal([Token.TK_MATH_MUL])
        elif self._token[1] == Token.TK_MATH_DIV:
            self._terminal([Token.TK_MATH_DIV])
        elif self._token[1] == Token.TK_MATH_ADD:
            self._terminal([Token.TK_MATH_ADD])
        elif self._token[1] == Token.TK_MATH_SUB:
            self._terminal([Token.TK_MATH_SUB])
        else:
            self._error = 'operacao_matematica_invalida'
            self._terminal()

    def _multiplication_seg(self):
        if self._token[1] in [Token.TK_MATH_MUL, Token.TK_MATH_DIV]:
            operador = self._token[1]
            self._mul_div_add_sub()

            if operador == Token.TK_MATH_DIV and self._token[0] == '0':
                self._error = 'division_by_zero'
                self._terminal()

            self._term()
            self._multiplication_seg()

    def _multiplication(self):
        self._term()
        self._multiplication_seg()

    def _add_sub_seg(self):
        if self._token[1] in [Token.TK_MATH_ADD, Token.TK_MATH_SUB]:
            self._mul_div_add_sub()
            self._multiplication()
            self._add_sub_seg()

    def _op_math(self):
        self._multiplication()
        self._add_sub_seg()

    def _chamada_seg(self):
        if self._token[1] == Token.TK_COMMA:
            self.__num_parametros += 1  # Contador o numero de parametros
            self._virgula()

            # Verifica se a variavel foi declarada
            if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
                self._error = 'undeclared_variable'
                self._terminal()

            self._identificador()
            self._chamada_seg()
        elif self._token[1] in [Token.TK_IDENT]:
            self._error = 'pontuacao'
            self._terminal(token=[Token.TK_COMMA])

    def _parametros_chamada_f(self):
        # Contador o numero de parametros
        self.__num_parametros += 1

        # Verifica se a variavel foi declarada
        if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
            self._error = 'undeclared_variable'
            self._terminal()

        self._identificador()
        self._chamada_seg()

    def _chama_funcao(self):
        self.__num_parametros = 0  # Contador de numeros de parametros

        self._id_funcao()

        # Verificação da existencia da funcao na atribuicao
        if not self.__functionSymbolTable.exists(name_function=self._token[0]):
            self._error = 'undeclared_function'
            self._terminal()

        # Nome da funcao - escopo
        self.__name_scope = self._token[0]

        # Tipo da funcao conforme o nome
        tipo = self.__functionSymbolTable.returnsTypeFunction(escopo=self.__name_scope)

        # Verificando o tipo da funçao - Compatibilidad3e
        if not self.__symbolTable.typeComparison(tipo, self.__varTypeAssign):
            self.__assignmentTypeError = tipo
            self._error = 'type_incompatible'
            self._terminal()

        self._identificador()
        self._open_p()
        if self._token[1] != Token.TK_CP:
            self._parametros_chamada_f()

        # Verificação de quantidade  de parâmetros na chamada da função
        if not self.__functionSymbolTable.checkNumberParameters(escopo=self.__name_scope, quant=self.__num_parametros):
            self._error = 'error_num_param'
            self._terminal()

        self._close_p()

    def _atribuicao(self):
        self._terminal([Token.TK_ASSIGNMENT])

    def _not(self):
        self._terminal([Token.TK_LOGIC_NOT])

    def _operador_l(self):  # OR, AND, DIF, LG, LE_GE, EQ
        if self._token[1] == Token.TK_LOGIC_OR:
            self._terminal([Token.TK_LOGIC_OR])
        elif self._token[1] == Token.TK_LOGIC_AND:
            self._terminal([Token.TK_LOGIC_AND])
        elif self._token[1] == Token.TK_LOGIC_DIF:
            self._terminal([Token.TK_LOGIC_DIF])
        elif self._token[1] == Token.TK_LOGIC_LG:
            self._terminal([Token.TK_LOGIC_LG])
        elif self._token[1] == Token.TK_LOGIC_LE_GE:
            self._terminal([Token.TK_LOGIC_LE_GE])
        elif self._token[1] == Token.TK_LOGIC_EQ:
            self._terminal([Token.TK_LOGIC_EQ])
        else:
            self._error = 'operacao_logica_invalida'
            self._terminal()

    def _op_logic(self):
        if self._token[1] == Token.TK_LOGIC_NOT:
            self._not()

        if self._token[1] == Token.TK_IDENT:
            # Verifica se a variavel foi declarada
            if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
                self._error = 'undeclared_variable'
                self._terminal()

            # Verifica compatibilidade de tipos
            tipo = self.__symbolTable.returnsTypeVariable(escopo=self.__escopo, identificador=self._token[0])

            # Tipo do operador logico 01
            self.__type_op_logic01 = tipo

            if not self.__symbolTable.typeComparison(tipo, self.__varTypeAssign) and not self.__op_logic_conditional:
                self.__assignmentTypeError = tipo
                self._error = 'type_incompatible'
                self._terminal()

            self._identificador()
        elif self._token[1] == Token.TK_NUMBER:

            # Tipo do operador logico 01
            self.__type_op_logic01 = Token.TK_INT

            # Verifica compatibilidade de tipos
            if not self.__symbolTable.typeComparison(Token.TK_INT, self.__varTypeAssign) and not self.__op_logic_conditional:
                self.__assignmentTypeError = self._token[1]
                self._error = 'type_incompatible'
                self._terminal()

            self._number()
        elif self._token[1] == Token.TK_REAL:

            # Tipo do operador logico 01
            self.__type_op_logic01 = Token.TK_FLOAT

            # Verifica compatibilidade de tipos
            if not self.__symbolTable.typeComparison(Token.TK_FLOAT, self.__varTypeAssign) and not self.__op_logic_conditional:
                self.__assignmentTypeError = self._token[1]
                self._error = 'type_incompatible'
                self._terminal()

            self._real()
        else:
            self._error = 'operacao_logica_invalida'
            self._terminal()

        self._operador_l()

        if self._token[1] == Token.TK_LOGIC_NOT:
            self._not()

        if self._token[1] == Token.TK_IDENT:
            # Verifica se a variavel foi declarada
            if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
                self._error = 'undeclared_variable'
                self._terminal()

            # Verifica compatibilidade de tipos
            tipo = self.__symbolTable.returnsTypeVariable(escopo=self.__escopo, identificador=self._token[0])

            # Tipo do operador logico 02
            self.__type_op_logic02 = tipo

            if not self.__symbolTable.typeComparison(tipo, self.__varTypeAssign) and not self.__op_logic_conditional:
                self.__assignmentTypeError = tipo
                self._error = 'type_incompatible'
                self._terminal()

            self._identificador()
        elif self._token[1] == Token.TK_NUMBER:

            # Tipo do operador logico 02
            self.__type_op_logic02 = Token.TK_INT

            # Verifica compatibilidade de tipos
            if not self.__symbolTable.typeComparison(Token.TK_NUMBER, self.__varTypeAssign) and not self.__op_logic_conditional:
                self.__assignmentTypeError = self._token[1]
                self._error = 'type_incompatible'
                self._terminal()

            self._number()
        elif self._token[1] == Token.TK_REAL:

            # Tipo do operador logico 02
            self.__type_op_logic02 = Token.TK_FLOAT

            # Verifica compatibilidade de tipos
            if not self.__symbolTable.typeComparison(Token.TK_FLOAT, self.__varTypeAssign) and not self.__op_logic_conditional:
                self.__assignmentTypeError = self._token[1]
                self._error = 'type_incompatible'
                self._terminal()

            self._real()
        else:
            self._error = 'operacao_logica_invalida'
            self._terminal()

    def _atribui_var(self):  # Exemplo -> a = b + 2  
        # Verifica se a variavel de atribuicao foi declarada
        if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
            self._error = 'undeclared_variable'
            self._terminal()

        # Atribui o tipo a ser feito na atribuicao
        self.__varTypeAssign = self.__symbolTable.returnsTypeVariable(self.__escopo, self._token[0])

        self._identificador()  # a
        self._atribuicao()  # =

        # Token que auxilia para qual metodo irá - Ve caractere futuro
        token_aux = self._proximo_tk()  # + 
        self._count -= 1  # Decrementa para voltar no token atual

        # Verifica se o caractere é NOT
        if self._token[1] == Token.TK_LOGIC_NOT:
            self._op_logic()
        # Valida se é operacao matematica
        elif token_aux[1] in self._operadores_matematicos:
            self._op_math()
        # Valida se é operacao logica
        elif token_aux[1] in self._operadores_logicos:
            self._op_logic()
        # Valida se é identificador/number/text/ident
        elif token_aux[1] == Token.TK_END:
            if self._token[1] == Token.TK_TEXT:
                # Verifica compatibilidade de tipos
                if not self.__symbolTable.typeComparison(Token.TK_STRING, self.__varTypeAssign):
                    self.__assignmentTypeError = self._token[1]
                    self._error = 'type_incompatible'
                    self._terminal()

                self._texto()
            elif self._token[1] == Token.TK_NUMBER:
                # Verifica compatibilidade de tipos
                if not self.__symbolTable.typeComparison(Token.TK_INT, self.__varTypeAssign):
                    self.__assignmentTypeError = self._token[1]
                    self._error = 'type_incompatible'
                    self._terminal()

                self._number()
            elif self._token[1] == Token.TK_REAL:
                # Verifica compatibilidade de tipos
                if not self.__symbolTable.typeComparison(Token.TK_FLOAT, self.__varTypeAssign):
                    self.__assignmentTypeError = self._token[1]
                    self._error = 'type_incompatible'
                    self._terminal()

                self._real()
            elif self._token[1] == Token.TK_IDENT:
                # Verifica se a variavel depois da atribuicao foi declarada
                if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
                    self._error = 'undeclared_variable'
                    self._terminal()

                # Verifica compatibilidade de tipos
                tipo = self.__symbolTable.returnsTypeVariable(escopo=self.__escopo, identificador=self._token[0])

                if not self.__symbolTable.typeComparison(tipo, self.__varTypeAssign):
                    self.__assignmentTypeError = tipo
                    self._error = 'type_incompatible'
                    self._terminal()

                self._identificador()
            else:
                self._error = "atribuicao_invalida"
                self._terminal()
        # Valida se é chamada de funcao
        elif self._token[1] == Token.TK_FUNC:
            self._chama_funcao()
        else:
            self._error = "atribuicao_invalida"
            self._terminal()

        self._ponto_virgula()

    def _declara_var(self):
        self._parametros()
        self._ponto_virgula()

    def _retorno(self):
        # Token corrente é diferente de TK_RETURN
        if self._token[1] != Token.TK_RETURN:
            self._error = 'no return'

        self._terminal([Token.TK_RETURN])

    def _real(self):
        self._terminal([Token.TK_REAL])

    def _number(self):
        self._terminal([Token.TK_NUMBER])

    def _texto(self):
        self._terminal([Token.TK_TEXT])

    def _ponto_virgula(self):
        if self._token[1] != Token.TK_END:
            self._error = 'pontuacao'

        self._terminal([Token.TK_END])

    def _tipos_retorno(self):
        if self._token[1] == Token.TK_IDENT:
            self._identificador()
        elif self._token[1] == Token.TK_REAL:
            self._real()
        elif self._token[1] == Token.TK_NUMBER:
            self._number()
        elif self._token[1] == Token.TK_TEXT:
            self._texto()
        else:
            self._error = 'retorno_vazio'
            self._terminal()

    def _retorno_f(self):
        self._retorno()

        # Caso seja identificador, verificar se foi declarada no seu escopo
        if self._token[1] == Token.TK_IDENT:
            if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
                self._error = 'undeclared_variable'
                self._terminal()

        # Tipo da funcao
        tipo = self._token[1]

        # CASO SEJA UM IDENTIFICADOR, RECUPERA DA TABELA DE SIMBOLOS O SEU TIPO
        if self._token[1] == Token.TK_IDENT:
            tipo = self.__symbolTable.returnsTypeVariable(escopo=self.__escopo, identificador=self._token[0])

        # Verifica se o retorno da funcao condiz com seu tipo de retorno
        if not self.__symbolTable.typeComparison(tipo_func=self.__retorno_func, tipo_var=tipo):
            self._error = 'tipo_retorno_invalido'
            self._terminal()

        self._tipos_retorno()
        self._ponto_virgula()

    def _id_funcao(self):
        self._terminal([Token.TK_FUNC])

    def _tipo(self):
        # Determinando o tipo da variavel
        self.__tipo = self._token[1]

        self._terminal(self._tipos)

    def _identificador(self):
        # Inicializa caracteristica do identificador
        self.__varName = self._token[0]
        # Cria um simbolo/variavel
        self.__symbol = Variable(self.__varName, self.__tipo)

        self._terminal([Token.TK_IDENT])

    def _open_p(self):
        # Token corrente é diferente de TK_OP
        if self._token[1] != Token.TK_OP:
            self._error = 'error_ok_op'

        self._terminal([Token.TK_OP])

    def _declara_par(self):
        self._tipo()
        self._identificador()

        self.__num_parametros += 1

        # Verifica se a variavel ja existe no escopo
        if not self.__symbolTable.exists(self.__escopo, self.__varName):
            # Adiciona na tabela
            self.__symbolTable.add(self.__escopo, self.__varName, self.__symbol)
        else:
            self._error = 'already_declared_variable'
            self._terminal()

    def _virgula(self):
        self._terminal([Token.TK_COMMA])

    def _parametro_seg(self):
        if self._token[1] == Token.TK_COMMA:
            self._virgula()
            self._declara_par()
            self._parametro_seg()

    def _parametros(self):
        # Verifica se o proximo caractere não é CP
        if not (self._token[1] == Token.TK_CP):
            self._declara_par()
            self._parametro_seg()

    def _close_p(self):
        # Token corrente é diferente de TK_CP
        if self._token[1] != Token.TK_CP:
            self._error = 'error_ok_op'

        self._terminal([Token.TK_CP])

    def _while(self):
        self._terminal([Token.TK_WHILE])

    def _laco(self):
        self._while()
        self._open_p()
        if self._token[1] != Token.TK_CP:
            # Ativa a flag como True para indicar operacao logica no contexto de condicional
            self.__op_logic_conditional = True

            self._op_logic()
        else:
            self._error = 'expressao_vazia'
            self._terminal()

        # Verificacao de compatibilidade de tipos da operacao
        if self.__type_op_logic01 != self.__type_op_logic02:
            self._error = 'logic_error'
            self._terminal()

        self._close_p()

        # Desaativa a flag
        self.__op_logic_conditional = False

        self._openKey()
        self._content()
        self._closeKey()

    def _print(self):
        self._terminal([Token.TK_PRINT])

    def _declara_print(self):
        self._print()
        self._open_p()

        if self._token[1] == Token.TK_TEXT:
            self._texto()
        elif self._token[1] == Token.TK_IDENT:
            # Verifica se a variavel foi declarada
            if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
                self._error = 'undeclared_variable'
                self._terminal()
            self._identificador()
        else:
            self._error = 'print_invalido'
            self._terminal()

        self._close_p()
        self._ponto_virgula()

    def _scanf(self):
        self._terminal([Token.TK_SCANF])

    def _declara_scanf(self):
        self._scanf()
        self._open_p()
        # Verifica se a variavel foi declarada
        if not self.__symbolTable.exists(escopo=self.__escopo, symbolName=self._token[0]):
            self._error = 'undeclared_variable'
            self._terminal()
        self._identificador()
        self._close_p()
        self._ponto_virgula()

    def _content(self):
        # Verifica se existe content no escopo
        if self._token[1] != Token.TK_CK:
            if self._token[1] in self._tipos:
                self._declara_var()
            elif self._token[1] == Token.TK_IDENT:
                self._atribui_var()
            elif self._token[1] == Token.TK_IF:
                self._condicional()
            elif self._token[1] == Token.TK_WHILE:
                self._laco()
            elif self._token[1] == Token.TK_PRINT:
                self._declara_print()
            elif self._token[1] == Token.TK_SCANF:
                self._declara_scanf()
            elif self._token == 'finish':
                self._terminal()
            elif not self._token[1] in self._conjunto_tokens_content:
                self._error = 'estado_invalido'
                self._terminal()

            if not self._token[1] in [Token.TK_CK, Token.TK_RETURN]:
                self._content()

    def _funcao(self):
        # ('BARBARIDADE', 'TK_FUNC', 1, 1)
        if self._token[1] != Token.TK_MAIN:
            self.__num_parametros = 0  # Reseta o numero de parametros

            self._id_funcao()

            # Inicializando o tipo da funcao
            self.__retorno_func = self._token[1]

            self._tipo()

            # Inicializando o name_function
            self.__escopo = self._token[0]

            # Verifica se a funcao já foi declarada
            if self.__functionSymbolTable.exists(name_function=self.__escopo):
                self._error = 'already_declared_function'
                self._terminal()

            # Insere a chave da funcao no dicionario da tabela de simbolos - variaveis
            self.__symbolTable.setKeyDict(self.__escopo)

            self._identificador()
            self._open_p()
            self._parametros()

            # =====================================
            # ADICIONA NA TABELA DE SIMBOLOS FUNCAO
            #   {'uberfunction': [retorno_func, num_parametros]}
            self.__functionSymbolTable.add(name_function=self.__escopo,
                                           info=[self.__retorno_func, self.__num_parametros])

            self._close_p()
            self._openKey()
            if self._token[1] != Token.TK_RETURN:
                self._content()
            self._retorno_f()
            self._closeKey()

            # Verifica se existem tokens para serem lidos
            if self._token != 'finish':
                self._funcao()

    def _openKey(self):
        # Token corrente é diferente de TK_OK
        if self._token[1] != Token.TK_OK:
            self._error = 'error_ok_op'

        self._terminal([Token.TK_OK])

    def _closeKey(self):
        # Token corrente é diferente de TK_CK
        if self._token[1] != Token.TK_CK:
            self._error = 'error_ok_op'

        self._terminal([Token.TK_CK])

    def _main(self):

        if self._token[1] == Token.TK_MAIN:  # verificar se o token atual e o TK_MAIN
            # Inicializando o name_function
            self.__escopo = self._token[0]
            # Insere a chave da funcao no dicionario 
            self.__symbolTable.setKeyDict(self.__escopo)

        self._terminal([Token.TK_MAIN])

    # ====================
    # MÉTODO PRINCIPAL - INICIO DA RECURSSÃO
    def _code(self):
        self._funcao()
        self._main()
        self._openKey()
        self._content()
        self._closeKey()

    #####################################################
    ############### METODOS DA CLASSE ###################
    #####################################################

    # ====================
    # INICIALIZACAO DA ANALISE SEMANTICA
    def analise_semantica(self):
        # Tente começar a analise, mas caso haja erro, lance uma exceção
        try:
            self._code()  # Inicia-se pelo code (raiz)
            print("Análise Semantica: [Concluido]")

            # Verifica se houve alguma variavel nao utilizada e notifica - Warning 
            self.__symbolTable.checkUsedVariables()

            return True  # Retorna True - Analise sintatica sucesso
        except Exception as error:
            print("Análise Semantica: [Gerando Erro]\n", end='')
            print(error)

            # Criando arquivo para os erros
            path_file_error = f"{sys.path[0]}/output_errors.txt"  # Diretorio para os arquivos de erros
            output_errors = open(path_file_error, 'w')

            # Gravando no arquivo
            output_errors.write(f'{error}')

            return False  # Retorna False - Analise sintatica falhou

    # ====================
    # ATRIBUI A SELF._TOKEN O PROXIMO TOKEN
    def _proximo_tk(self):
        temp = 'finish'  # De inicio é atribuido temp como 'finish'

        # Caso o count ainda seja menor que a lista de tokens, redefine temp
        if self._count < len(self._table_tokens):
            temp = self._table_tokens[self._count]
            self._count += 1  # O count ja fica posicionado para o proximo token
        return temp

    # ====================
    # GET DA TABELA DE SIMBOLOS - VARIAVEIS
    def getSymbolTableVariables(self):
        return self.__symbolTable

    # ====================
    # GET DA TABELA DE SIMBOLOS - FUNCAO
    def getSymbolTableFunction(self):
        return self.__functionSymbolTable
