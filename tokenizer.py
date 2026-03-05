from models import Token, TokenType, State_tokenizer

class Tokenizer:
    def __init__(self, text):
        self.text = text #výchozí text pro tokenizaci
        self.state = State_tokenizer.DATA #počáteční stav tokenizéru
        self.tokens = [] #výstupní seznam tokenů
        self.buffer = "" #pomocný buffer pro shromažďování znaků pro aktuální token
        self.attribute_name = "" #pomocný buffer pro shromažďování znaků pro název atributu
        self.attribute_value = "" #pomocný buffer pro shromažďování znaků pro hodnotu atributu
        self.attribute_list = {} #pomocný slovník pro shromažďování atributů aktuálního tagu
        self.attribute_close_char = None #pomocná proměnná pro určení, zda se nacházíme uvnitř uvozovek pro hodnotu atributu
        self.ATTRIBUTES_OPTIONS = ("href", "id", "class") #seznam atributů, které nás zajímají a které budeme ukládat do tokenů

    def emit(self, token_type): #vytvoření nového tokenu
        self.tokens.append(Token(token_type, self.buffer, attributes=self.attribute_list.copy()))
        self.buffer = ""
        self.attribute_name = ""
        self.attribute_value = ""
        self.attribute_list = {}
        self.attribute_close_char = None

    def tokenize(self): #stavový automat pro vytvoření tokenů a jejich otypování
        for ch in self.text:
            match self.state:
                case State_tokenizer.DATA: #zápis textu, přechod do zpracování tagů
                    if ch == "<":
                        if self.buffer:
                            self.emit(TokenType.TEXT)
                        self.state = State_tokenizer.TAG_OPEN
                    else:
                        self.buffer += ch
                case State_tokenizer.TAG_OPEN: #zpracování tagů, přechod do zpracování názvu tagu nebo koncového tagu
                    if ch == "/":
                        self.state = State_tokenizer.END_TAG_OPEN
                    else:
                        self.buffer = ch
                        self.state = State_tokenizer.TAG_NAME
                case State_tokenizer.TAG_NAME: #zpracování názvu tagu, přechod do zpracování atributů nebo konce tagu
                    if ch == ">":
                        if self.buffer[0] != "!":
                            self.emit(TokenType.START_TAG)
                        self.state = State_tokenizer.DATA
                    elif ch.isspace() or ch == "/":
                        self.state = State_tokenizer.ATTRIBUTE_NAME
                    else:
                        self.buffer += ch
                case State_tokenizer.END_TAG_OPEN: #zpracování koncového tagu, přechod do zpracování názvu tagu
                    if ch == ">":
                        self.emit(TokenType.END_TAG)
                        self.state = State_tokenizer.DATA
                    else:
                        self.buffer += ch
                case State_tokenizer.ATTRIBUTE_NAME: #zpracování názvu atributu, přechod do zpracování hodnoty atributu, nebo nového tokenu
                    if ch == "=":
                        self.state = State_tokenizer.ATTRIBUTE_VALUE
                    elif ch == ">":
                        self.emit(TokenType.START_TAG)
                        self.state = State_tokenizer.DATA
                    elif ch.isspace():
                        pass
                    else:
                        self.attribute_name += ch
                case State_tokenizer.ATTRIBUTE_VALUE: #zpracování hodnoty atributu, přechod do zpracování dalšího atributu nebo konce tagu
                    if self.attribute_close_char == None:    
                        if ch in ('"', "'"):
                            self.attribute_close_char = ch
                    elif ch == self.attribute_close_char:
                        if self.attribute_name in self.ATTRIBUTES_OPTIONS:
                            self.attribute_list[self.attribute_name] = self.attribute_value
                            self.attribute_name, self.attribute_value = "",""
                            self.attribute_close_char = None
                            self.state = State_tokenizer.TAG_NAME                            
                        else:
                            self.attribute_name, self.attribute_value = "",""
                            self.attribute_close_char = None
                            self.state = State_tokenizer.TAG_NAME
                    else:
                        self.attribute_value += ch
                   
        return self.tokens #vrácení seznamu tokenů po dokončení tokenizace