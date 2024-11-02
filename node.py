class Node:
    def __init__(self) -> None:
        # usar lexema
        # Datos reales
        self.child = [None, None, None]
        self.siblings = []
        self.lineno = None

        # node_kind:
        # 0 (Tipos de Nodo): MAIN | EXPRESION | SENTENCIA | DECLARACION
        # 1 (Tipos de exp):  OPERADOR | CONSTANTE | IDENTIFICADOR
        # 1 (Tipos de sent): SELECCION | ITERACION | REPETICION | IN | OUT | ASIGNACION
        # 1 (Tipos de dec):  INTEGER | DOUBLE
        self.node_kind = [None, None]

        # Lexema
        # Datos a mostrar en el arbol
        self.name = None
        self.op = None
        self.val = None

        # INTEGER, DOUBLE, VOID, BOOLEAN
        self.exp_type = None

    def preorden(self):
        print(f"N: {self.name}, T: {self.exp_type}, V:{self.val}")
        for node in self.child:
            if node == None:
                break
            else:
                node.preorden()

        for node in self.siblings:
            node.preorden()

    def to_dict(self):
        res = {"name": self.name}

        if self.node_kind[0] == "EXPRESION":
            res["attributes"] = [
                {
                    "type": f"Tipo: {str(self.exp_type)}",
                    "value": f"Valor: {str(self.val)}",
                }
            ]

        # if self.node_kind[0] == 'DECLARACION':
        #     res["attributes"] = [{"type": str(self.exp_type)}]

        children = []
        siblings = []

        # for node in self.child:
        #     if node == None:
        #         break
        #     else:
        #         children.append(node.to_dict())
        for node in self.child:
            if node != None:
                children.append(node.to_dict())

        for node in self.siblings:
            siblings.append(node.to_dict())

        if children != []:
            res["children"] = children

        if siblings != []:
            res["siblings"] = siblings

        return res

    def to_dict_attr(self):
        # res = {
        #     "name": self.name
        # }

        if self.node_kind[0] == "EXPRESION":
            res = {"name": f"{self.name}, T: {str(self.exp_type)}, V: {str(self.val)}"}
            # res["attributes"] = [{"type": f'Tipo: {str(self.exp_type)}', "value": f'Valor: {str(self.val)}'}]
        elif self.node_kind[1] == "ASIGNACION":
            res = {"name": f"{self.name}, T: {str(self.exp_type)}, V: {str(self.val)}"}
        else:
            res = {"name": self.name}

        # if self.node_kind[0] == 'DECLARACION':
        #     res["attributes"] = [{"type": str(self.exp_type)}]

        children = []
        siblings = []

        # for node in self.child:
        #     if node == None:
        #         break
        #     else:
        #         children.append(node.to_dict())
        for node in self.child:
            if node != None:
                children.append(node.to_dict_attr())

        for node in self.siblings:
            siblings.append(node.to_dict_attr())

        if children != []:
            res["children"] = children

        if siblings != []:
            res["siblings"] = siblings

        return res
