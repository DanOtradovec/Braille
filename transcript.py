from models import BrailleModel

class Transcript:
    def __init__(self, text):
        self.text = text #vstupní text pro převod do Braille
        self.buffer = "" #pomocný buffer pro shromažďování znaků pro aktuální řádek Braille
        self.line = "" #aktuální řádek Braille, který se bude přidávat do výstupního seznamu řádků
        self.lines = [] #výstupní seznam řádků Braille

    def add_line(self): #metoda pro přidání aktuálního řádku do výstupního seznamu
        line = self.line.strip()
        if ((len(self.lines)+1)%BrailleModel.page_lines) == 0: #zajištění oddělení stránek
            line += '\f'
        self.lines.append(line)
        self.line = ""

    def to_braille(self):
        brail_text = ""
        for ch in self.text: #převedení do Braille pomocí slovníku pro českou Brailleovou zkratkovou abecedu
            if ch in BrailleModel.czech_brf.keys():
                brail_text += BrailleModel.czech_brf[ch]
        for ch in brail_text: #rozdělení do řádků a stránek
            if len(self.buffer) >= BrailleModel.page_width: #ošetření slov, která by přesahovala šířku stránky
                self.line += self.buffer
                self.add_line()
                self.buffer = ""
            elif ch in (' ','\n') and (len(self.line)+len(self.buffer)) >= BrailleModel.page_width: #ošetření zalomení řádku
                self.add_line()                

            if ch == ' ':
                self.line += self.buffer + ' '
                self.buffer = ""
            elif ch == '\n':
                self.line += self.buffer
                self.add_line()
                self.add_line()
                self.buffer = ""
            else:
                self.buffer += ch
        if self.buffer or self.line: #ošetření zapsání zbytku textu, pokud nebyl přidán
            if (len(self.line)+len(self.buffer)) >= BrailleModel.page_width:
                self.add_line()
            self.line += self.buffer
            self.add_line()
        return '\n'.join(self.lines)

    def visualize(self, text): #vizualizace do Braille (tečky)
        brail_visualisation = ""
        for ch in text:
            if ch in BrailleModel.brf_to_dots.keys():
                brail_visualisation += BrailleModel.brf_to_dots[ch]
        return brail_visualisation