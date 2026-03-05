from models import ElementNode, TextNode, BuilderModel, TokenType

#tvorba DOM - implementovaný pruning a flattening
class DOMbuilder:
    def __init__(self, tokens):
        self.tokens = tokens #výchozí seznam tokenů pro tvorbu DOM stromu
        self.root = ElementNode("root") #kořenový uzel DOM stromu, který bude obsahovat všechny ostatní uzly jako své potomky
        self.stack = [self.root] #zásobník pro sledování aktuálního umístění v DOM stromu během jeho tvorby, začíná s kořenovým uzlem
        self.ignoring_tag = "" #proměnná pro sledování, zda se nacházíme uvnitř ignorovaného tagu

    def normalyze(self, text): #funkce pro nahrazení HTML entit jejich skutečnými znaky
        for key, value in BuilderModel.replacement.items():
            text = text.replace(key, value)
        return text

    def built(self): #funkce pro vytvoření DOM stromu z tokenů, implementuje pruning a flattening
        currentNode = self.root       
        for token in self.tokens:
            if self.ignoring_tag:
                if token.type == TokenType.END_TAG and token.value == self.ignoring_tag:
                    self.ignoring_tag = ""
                continue

            if token.type == TokenType.START_TAG:  #zpracování startovacího tagu, nový uzel DOM stromu
                if token.value in BuilderModel.VOID_TAGS: #zpracování void tagů, přidáno jako potomek aktuálního uzlu, ale nepokračujeme "v něm"
                    newNode = ElementNode(token.value)
                    newNode.attributes = getattr(token, "attributes", {})
                    newNode.parent_node = self.stack[-1]
                    self.stack[-1].children.append(newNode)
                elif token.value in BuilderModel.NOISE_TAGS: #zpracování noise tagů, ignorování obsahu až do konce tohoto tagu
                    self.ignoring_tag = token.value
                elif token.value in BuilderModel.STYLE_TAGS: #zpracování style tagů, nevytváří se uzel pro tento tag, ale neignorujeme jeho obsah,
                    continue
                else:
                    newNode = ElementNode(token.value) #zpracování ostatních tagů, vytvoření nového uzlu a posunutí o úroveň níž v DOM
                    newNode.attributes = getattr(token, "attributes", {})
                    if token.value == "head":
                        self.root.head_node = newNode
                    newNode.parent_node = self.stack[-1]
                    self.stack[-1].children.append(newNode)
                    self.stack.append(newNode)
            elif token.type == TokenType.END_TAG and token.value not in (BuilderModel.STYLE_TAGS | BuilderModel.VOID_TAGS): #zpracování koncového tagu, posunutí o úroveň výš v DOM
                if len(self.stack) > 1:    
                    self.stack.pop()
            elif token.type == TokenType.TEXT: #zpracování textu, vytvoření koncového - textového uzlu
                token.value = self.normalyze("".join(token.value.strip()))
                if token.value:
                    textNode = TextNode(token.value)
                    self.stack[-1].children.append(textNode)
        return self.root #vrácení DOM - kořenový uzel obsahuje všechny ostatní uzly jako potomky