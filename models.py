#Vytvoření statických tříd
from dataclasses import dataclass, field
from enum import Enum

class TokenType(Enum): #typ tokenu
    START_TAG = "START_TAG"
    END_TAG = "END_TAG"
    TEXT = "TEXT"

@dataclass
class Token: #token
    type: TokenType
    value: str
    attributes: dict = field(default_factory = dict)

class State_tokenizer: #stav tokenizéru
    DATA = "DATA"
    TAG_OPEN = "TAG_OPEN"
    TAG_NAME = "TAG_NAME"
    END_TAG_OPEN = "END_TAG_OPEN"
    ATTRIBUTE_VALUE = "ATTRIBUTE_VALUE"
    ATTRIBUTE_NAME = "ATTRIBUTE_NAME"


class Node: #mateřská třída všech prvků DOM
    def __init__(self):
        pass

class ElementNode(Node): #uzly DOM
    def __init__(self, tag_name):
        self.children = []
        self.parent = None
        self.tag_name = tag_name
        self.text_length = 0
        self.link_text_length = 0
        self.density_link = 0.0
        self.density_interpunction = 0
        self.head_node = None

class TextNode(Node): #koncové prvky DOM - vlastní text
    def __init__(self, text):
        self.text = text
        self.text_length = len(text)

class State_transcript: #stav transcriptoru do .brf
    TEXT = "TEXT"
    SPACE = "SPACE"
    NEW_LINE = "NEW_LINE"

class BuilderModel:
    NOISE_TAGS = {"nav", "footer", "header", "aside", "script", "style", "nonscript", "iframe", "form", "svg"} #sada tagů, u kterých ignorujeme obsah
    STYLE_TAGS = {"b", "i", "u", "strong", "em", "span", "small", "sub", "sup"} #sada tagů, které samy ignorujeme, ale jejich obsah zahrnemem do DOM
    VOID_TAGS = {"br", "img", "hr", "meta", "link", "input", "!DOCTYPE", "!--"} #sada tagů, u kterých se neočekává uzavírací tag, nemají potomky
    replacement = {
    "&quot;": '"',
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&nbsp;": " ",
    "&apos;": "'",
    "&x27;": "'",
    "&#x27;": "'",
    "&ndash;": "-",
    "&mdash;": "-",
    "&lsquo;": "'",
    "&rsquo;": "'",
    "&ldquo;": '"',
    "&rdquo;": '"',
    "&bdquo;": '"',
    "&hellip;": "...",
    "&copy;": "(c)",
    "&reg;": "(r)",
    "&trade;": "(tm)",
    "&euro;": "EUR",
    
    "\xa0": " ",
    "\u2013": "-",
    "\u2014": "-",
    "\u201c": '"',
    "\u201d": '"',
    "\u201e": '"',
    "\u2018": "'",
    "\u2019": "'",
    "\u201a": "'",
    "\u2026": "...",
    "\u200b": "",
    }#slovník pro nahrazení HTML entit jejich skutečnými znaky

class BrailleModel:
    page_width = 40
    page_lines = 25
    czech_brf  = {
    # Mezera
    ' ': ' ',
    '\n': '\n',
    # MALÁ PÍSMENA (Standardní ASCII)
    'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h', 
    'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 
    'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 
    'y': 'y', 'z': 'z',
    # VELKÁ PÍSMENA (S předznakem čárka ',')
    'A': ',a', 'B': ',b', 'C': ',c', 'D': ',d', 'E': ',e', 'F': ',f', 'G': ',g', 'H': ',h', 
    'I': ',i', 'J': ',j', 'K': ',k', 'L': ',l', 'M': ',m', 'N': ',n', 'O': ',o', 'P': ',p', 
    'Q': ',q', 'R': ',r', 'S': ',s', 'T': ',t', 'U': ',u', 'V': ',v', 'W': ',w', 'X': ',x', 
    'Y': ',y', 'Z': ',z',
    # ČESKÁ DIAKRITIKA (Malá)
    'á': '(', 'č': '*', 'ď': '<', 'é': 'e', 'ě': '2', 'í': 'i', 
    'ň': 'n', 'ó': 'o', 'ř': 'r', 'š': '%', 'ť': 't', 'ú': 'u', 
    'ů': 'u', 'ý': 'y', 'ž': 'z',
    # ČESKÁ DIAKRITIKA (Velká - s předznakem)
    'Á': ',(', 'Č': ',*', 'Ď': ',<', 'É': ',e', 'Ě': ',2', 'Í': ',i', 
    'Ň': ',n', 'Ó': ',o', 'Ř': ',r', 'Š': ',%', 'Ť': ',t', 'Ú': ',u', 
    'Ů': ',u', 'Ý': ',y', 'Ž': ',z',
    # ČÍSLA
    '1': '#a', '2': '#b', '3': '#c', '4': '#d', '5': '#e', 
    '6': '#f', '7': '#g', '8': '#h', '9': '#i', '0': '#j',
    # INTERPUNKCE
    '.': '4',
    ',': '1',
    ';': '2',
    ':': '3',
    '!': '6',
    '?': '0',
    '"': '8',
    '\'': "'",
    '-': '-',
    '/': '/',
    '(': '7',
    ')': 'g',
    }

    brf_to_dots = {
    # Mezera a řídicí znaky (ty zůstávají, aby fungovalo formátování)
    ' ': '⠀', '\n': '\n', '\f': '\f',
    
    # MALÁ PÍSMENA (Standardní mezinárodní ASCII Braille)
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠗',
    'i': '⠊', 'j': '⠚', 'k': '⠇', 'l': '⠸', 'm': '⠽', 'n': '⠝', 'o': '⠕', 'p': '⠏',
    'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
    'y': '⠽', 'z': '⠵',

    # PŘEDZNAKY
    ',': '⠠',  # Velké písmeno (bod 6)
    '#': '⠼',  # Číselný znak (body 3456)

    # ČESKÁ DIAKRITIKA (Mapování podle tvých values v ceska_brf)
    '(': '⠷',  # á (body 12356)
    '*': '⠱',  # č (body 1456)
    '<': '⠣',  # ď (body 126)
    '2': '⠒',  # ě (body 25) - pozor, u tebe v interpunkci je to středník
    '%': '⠩',  # š (body 146)
    
    # INTERPUNKCE (Mapování podle tvých values v ceska_brf)
    '4': '⠲',  # tečka . (body 256)
    '1': '⠂',  # čárka , (bod 2)
    '3': '⠇',  # dvojtečka : (body 123)
    '6': '⠖',  # vykřičník ! (body 235)
    '0': '⠴',  # otazník ? (body 356)
    '8': '⠦',  # uvozovky " (body 236)
    "'": '⠄',  # apostrof ' (bod 3)
    '-': '⠤',  # spojovník - (body 36)
    '/': '⠌',  # lomítko / (body 34)
    '7': '⠗',  # levá závorka ( (v tvém slovníku body 1235)
    } #slovník pro vizualizaci českého .brf pomocí ascii znaků pro braille