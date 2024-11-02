import json
import os
from node import Node

class AnalizadorSemantico:
    def __init__(self, arbol_sintactico) -> None:
        self.arbol_sintactico = arbol_sintactico
        self.tabla_simbolos = {}
        self.errores = []
    
    def analisis_semantico(self):
        if self.arbol_sintactico is not None:
            self.preorden(self.arbol_sintactico)
        
        return self.arbol_sintactico, self.tabla_simbolos, self.errores
        
        # print(self.errores)
        # print(self.tabla_simbolos)
        # self.arbol_sintactico_anotado.preorden()
    
    def preorden(self, nodo: Node, parent_node_kind = [None,None]):
        # Este primer condicional puede ser ajustado a la logica de todos los demas condicionales
        # Evaluar el nodo actual y en lugar de llamar un preorden para los hijos
        # obtener directamente cada varible y modificarla desde el padre
        if parent_node_kind[0] == 'DECLARACION':
            if nodo.node_kind[1] == 'IDENTIFICADOR':
                if nodo.name not in self.tabla_simbolos:
                    self.tabla_simbolos[nodo.name] = {'type':nodo.exp_type, 'value':nodo.val, 'loc': len(self.tabla_simbolos)+1, 'lines': [nodo.lineno]}
                else:
                    error = f'Error en la linea {nodo.lineno}: la variable "{nodo.name}" ya esta declarada en la linea {self.tabla_simbolos[nodo.name]["lines"][0]}'
                    self.errores.append(error)
            
            for child in nodo.child:
                if child == None:
                    break
                else:
                    self.preorden(child, nodo.node_kind)
            
            for sibling in nodo.siblings:
                self.preorden(sibling, nodo.node_kind)
        
        elif nodo.node_kind[0] == 'SENTENCIA':
            if nodo.node_kind[1] == 'ASIGNACION':
                identificador: Node = nodo.child[0]
                if identificador.name in self.tabla_simbolos:
                    self.tabla_simbolos[identificador.name]["lines"].append(identificador.lineno)
                    identificador.exp_type = self.tabla_simbolos[identificador.name]["type"]
                    
                    valor, tipo = self.preorden(nodo.child[1])
                    nodo.val = valor
                    nodo.exp_type = tipo
                    if tipo == None:
                        self.tabla_simbolos[identificador.name]["value"] = None
                        identificador.val = None
                    elif tipo == 'boolean':
                        self.tabla_simbolos[identificador.name]["value"] = None
                        identificador.val = None
                        error = f'Error en la linea {nodo.lineno}: no se puede asignar un valor "{tipo}" a una variable "{identificador.exp_type}"'
                        self.errores.append(error)
                    elif tipo == 'integer':
                        if identificador.exp_type == 'integer':
                            self.tabla_simbolos[identificador.name]["value"] = int(valor)
                            identificador.val = int(valor)
                        else:
                            self.tabla_simbolos[identificador.name]["value"] = float(valor)
                            identificador.val = float(valor)
                            
                    elif tipo == 'double':
                        if identificador.exp_type == 'double':
                            self.tabla_simbolos[identificador.name]["value"] = float(valor)
                            identificador.val = float(valor)
                        else:
                            error = f'Error en la linea {nodo.lineno}: no se puede asignar un valor "{tipo}" a una variable "{identificador.exp_type}"'
                            self.errores.append(error)
                else:
                    error = f'Error en la linea {identificador.lineno}: la variable "{identificador.name}" no se ha declarado'
                    self.errores.append(error)
            elif nodo.node_kind[1] == 'SELECCION' or nodo.node_kind[1] == 'ITERACION':
                # Validar que child[0] sea exp boolean
                exp_valor, exp_tipo = self.preorden(nodo.child[0])
                if exp_tipo != 'boolean':
                    error = f'Error en la linea {nodo.lineno}: sentencia {nodo.name} espera una expresion "boolean", recibió una expresion "{exp_tipo}'
                    self.errores.append(error)
                
                # Ejecutar preorden para nodo then (si existe)
                if nodo.child[1] is not None:
                    self.preorden(nodo.child[1])
                
                # Ejecutar preorden para nodo else (si existe)
                if nodo.child[2] is not None:
                    self.preorden(nodo.child[2])
                
            elif nodo.node_kind[1] == 'REPETICION':
                # Ejecutar preorden nodo then (si existe)
                if nodo.child[0] is not None:
                    self.preorden(nodo.child[0])
                
                # Validar que child[1] sea exp boolean
                exp_valor, exp_tipo = self.preorden(nodo.child[1])
                if exp_tipo != 'boolean':
                    error = f'Error en la linea {nodo.lineno}: sentencia {nodo.name} espera una expresion "boolean", recibió una expresion "{exp_tipo}'
                    self.errores.append(error)
                
            else:
                for child in nodo.child:
                    if child == None:
                        break
                    else:
                        self.preorden(child, nodo.node_kind)
                
                for sibling in nodo.siblings:
                    self.preorden(sibling, nodo.node_kind)
        elif nodo.node_kind[0] == 'EXPRESION':
            if nodo.node_kind[1] == 'CONSTANTE':
                return nodo.val, nodo.exp_type
            
            elif nodo.node_kind[1] == 'IDENTIFICADOR':
                if nodo.name in self.tabla_simbolos:
                    if nodo.lineno is not None:
                        self.tabla_simbolos[nodo.name]["lines"].append(nodo.lineno)
                    valor = self.tabla_simbolos[nodo.name]['value']
                    nodo.val = valor
                    nodo.exp_type = self.tabla_simbolos[nodo.name]["type"]
                    if valor is None:
                        error = f'Error en la linea {nodo.lineno}: la variable "{nodo.name}" no se ha inicializado'
                        self.errores.append(error)
                else:
                    error = f'Error en la linea {nodo.lineno}: la variable "{nodo.name}" no se ha declarado'
                    self.errores.append(error)
                return nodo.val, nodo.exp_type
            
            elif nodo.node_kind[1] == 'OPERADOR':
                valor_op_0, tipo_op_0 = self.preorden(nodo.child[0])
                valor_op_1, tipo_op_1 = self.preorden(nodo.child[1])
                # op_log ['AND','OR']
                # op_rel ['MENOR','MENOR_IGUAL','MAYOR','MAYOR_IGUAL','DIFERENTE','IGUAL']
                # op_sum ['SUMA','RESTA']
                # op_mul ['MULTIPLICACION','DIVISION','MODULO']
                # op_pot ['POTENCIA']
                
                if nodo.op in ['AND','OR']:
                    nodo.exp_type = 'boolean'
                    if tipo_op_0 == 'boolean' and tipo_op_1 == 'boolean':
                        if valor_op_0 is not None and valor_op_1 is not None:
                            # Efectuar operacion
                            if nodo.op == 'AND':
                                nodo.val = valor_op_0 and valor_op_1
                            else:
                                nodo.val = valor_op_0 or valor_op_1
                        else:
                            error = f'Error en la linea {nodo.lineno}: operacion logica "{valor_op_0} {nodo.name} {valor_op_1}" no permitida'
                            self.errores.append(error)
                            nodo.val = None
                    else:
                        error = f'Error en la linea {nodo.lineno}: operacion logica entre tipos de datos "{tipo_op_0}" y "{tipo_op_1}" no permitida'
                        self.errores.append(error)
                        nodo.val = None
                    
                elif nodo.op in ['MENOR','MENOR_IGUAL','MAYOR','MAYOR_IGUAL','DIFERENTE','IGUAL']:
                    nodo.exp_type = 'boolean'
                    if tipo_op_0 in ['integer','double'] and tipo_op_1 in ['integer','double']:
                        if valor_op_0 is not None and valor_op_1 is not None:
                            # Efectuar operacion
                            if nodo.op == 'MENOR':
                                nodo.val = valor_op_0 < valor_op_1
                            elif nodo.op == 'MENOR_IGUAL':
                                nodo.val = valor_op_0 <= valor_op_1
                            elif nodo.op == 'MAYOR':
                                nodo.val = valor_op_0 > valor_op_1
                            elif nodo.op == 'MAYOR_IGUAL':
                                nodo.val = valor_op_0 >= valor_op_1
                            elif nodo.op == 'DIFERENTE':
                                nodo.val = valor_op_0 != valor_op_1
                            else:
                                nodo.val = valor_op_0 == valor_op_1
                        else:
                            error = f'Error en la linea {nodo.lineno}: operacion relacional "{valor_op_0} {nodo.name} {valor_op_1}" no permitida'
                            self.errores.append(error)
                            nodo.val = None
                    else:
                        error = f'Error en la linea {nodo.lineno}: operacion relacional entre tipos de datos "{tipo_op_0}" y "{tipo_op_1}" no permitida'
                        self.errores.append(error)
                        nodo.val = None
                    # return nodo.val, nodo.exp_type
                
                elif nodo.op in ['SUMA','RESTA','MULTIPLICACION','DIVISION','MODULO','POTENCIA']:
                    if tipo_op_0 in ['integer','double'] and tipo_op_1 in ['integer','double']:
                        if valor_op_0 is not None and valor_op_1 is not None:
                            if nodo.op == 'SUMA':
                                nodo.val = valor_op_0 + valor_op_1
                            elif nodo.op == 'RESTA':
                                nodo.val = valor_op_0 - valor_op_1
                            elif nodo.op == 'MULTIPLICACION':
                                nodo.val = valor_op_0 * valor_op_1
                            elif nodo.op == 'DIVISION':
                                nodo.val = valor_op_0 / valor_op_1
                            elif nodo.op == 'MODULO':
                                nodo.val = valor_op_0 % valor_op_1
                            else:
                                nodo.val = valor_op_0 ** valor_op_1
                            
                            if tipo_op_0 == 'integer' and tipo_op_1 == 'integer':
                                nodo.val = int(nodo.val)
                            
                            if type(nodo.val) == int:
                                nodo.exp_type = 'integer'
                            elif type(nodo.val) == float:
                                nodo.exp_type = 'double'
                        else:
                            error = f'Error en la linea {nodo.lineno}: operacion aritmetica "{valor_op_0} {nodo.name} {valor_op_1}" no permitida'
                            self.errores.append(error)
                            nodo.val = None
                    else:
                        error = f'Error en la linea {nodo.lineno}: operacion artimetica entre tipos de datos "{tipo_op_0}" y "{tipo_op_1}" no permitida'
                        self.errores.append(error)
                        nodo.val = None
                        nodo.exp_type = 'integer'
                    
                return nodo.val, nodo.exp_type
                    
                # return None, None
        #     return 2
        else:
            for child in nodo.child:
                if child == None:
                    break
                else:
                    self.preorden(child, nodo.node_kind)
            
            for sibling in nodo.siblings:
                self.preorden(sibling, nodo.node_kind)
    
    def tree_to_json(self,root):
        # Agregar root y array
        diccionario = {
            'main': [root.to_dict_attr()]
        }
        # diccionario = root.to_dict()
        
        json_tree = json.dumps(diccionario, indent=2)
        self.escribir_json(json_tree)

    def escribir_json(self,json_tree):
        parent_directory = os.path.dirname(__file__)
        dirname = 'analisis_semantico'
        abs_dir = os.path.join(parent_directory,dirname)
        filename = 'tree.json'

        if os.path.isdir(abs_dir):
            abs_path = os.path.join(abs_dir,filename)
            with open(abs_path, 'w') as archivo:
                archivo.write(json_tree)
        else:
            try:
                os.mkdir(abs_dir)
                abs_path = os.path.join(abs_dir,filename)
                with open(abs_path, 'w') as archivo:
                    archivo.write(json_tree)
            except:
                print(f'Error al trabajar en el directorio: {abs_dir}')
                pass
    