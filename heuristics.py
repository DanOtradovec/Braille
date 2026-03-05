from domBuilder import ElementNode, TextNode

class Heuristic:
    def __init__(self, root):
        self.root = root #kořenový uzel DOM stromu, vstup pro heuristiku
        self.delimiters = ("|", "-", "\u2013", "\u2014", "\u2022", "\xb7", "\xbb", "\xa0") #sada oddělovačů pro rozdělení title tagu
        self.final_text = "" #výstupní text, obsahuje extrahovaný článek
        #parametry pro hodnocení uzlů
        self.weigth_len = 0.1
        self.weigth_inter = 10
        self.weight_link = 2
        self.parent_disadvantage = 0.5 #faktor pro zvýhodnění hlubších uzlů

    def analyze(self, node, inside_link = False): #rekurzivní fuknce pro zjištění parametrů pro hodnocení uzlů
        current_inside_link = inside_link or node.tag_name == "a" #kontrola, zda se nacházíme uvnitř odkazu
        total_text = 0 #celková délka textu v potomcích tohoto uzlu
        link_text = 0 #celková délka textu v odkazech v potomcích tohoto uzlu
        interpunction = 0 #vážený počet interpunction znaků v potomcích tohoto uzlu

        for child in node.children:
            if isinstance(child, TextNode): #zpracování textového uzlu, aktualizace parametrů pro hodnocení
                total_text += child.text_length
                interpunction += sum(1 for ch in child.text if ch in (".,"))
                interpunction += sum(0.8 for ch in child.text if ch in ("?!"))
                interpunction += sum(0.4 for ch in child.text if ch in (":;"))
                if current_inside_link:
                    link_text += child.text_length

            elif isinstance(child, ElementNode): #rekurzivní zpracování potomků, které jsou uzly DOM, aktualizace parametrů pro hodnocení
                child_total, child_link, child_inter = self.analyze(child, current_inside_link)
                total_text += child_total
                link_text += child_link
                interpunction += child_inter
        #nastavení parametrů pro hodnocení tohoto uzlu
        node.text_length = total_text
        node.link_text_length = link_text
        node.density_link = (link_text / total_text) if total_text > 0 else 0.0
        node.density_interpunction = (100*interpunction / total_text) if total_text > 0 else 0.0
        return total_text, link_text, interpunction #vrácení parametrů, které budou použity pro hodnocení rodičovských uzlů

    def get_text(self, node): #rekurzivní funkce pro získání textu ze všech potomků uzlu, vytvoření výstupního textu
        final_text = "" #výstupní text pro tento uzel a jeho potomky
        if isinstance(node, TextNode): #zpracování textového uzlu
            final_text += node.text + "\n"
        elif isinstance(node, ElementNode): #rekurzivní zpracování potomků, které jsou uzly DOM
            for child in node.children:
                final_text += self.get_text(child)
        return final_text #vrácení surového textu pro potomky tohoto uzlu
    
    def evaluate(self, node): #funkce pro výpočet skóre pro tento uzel na základě jeho parametrů, které byly zjištěny funkcí analyze
        score = (node.text_length*self.weigth_len)*(node.density_interpunction*self.weigth_inter)*((1-node.density_link)**self.weight_link)
        return score

    def find_best_node(self, node): #rekurzivní funkce pro nalezení uzlu s nejvyšším skóre, který bude považován za hlavní obsah stránky
        best_child = None
        max_score = -1
        for child in node.children: #porovnání skóre tohoto uzlu s jeho potomky
            if isinstance(child, ElementNode):
                child_score = self.evaluate(child)
                if child_score > max_score:
                    max_score = child_score
                    best_child = child
        if max_score > (self.evaluate(node)*self.parent_disadvantage): #porovnání nejlepšího potomka s tímto uzlem
            return self.find_best_node(best_child) #rekurzivní pokračování hledání (do hloubky)
        return node #vrácení tohot uzlu, pokud je lepší než jeho nejlepší potomek

    def find_title_head(self, node): #hledání nadpisu pomocí title tagu v head části DOM
        for child in node.head_node.children:
            if isinstance(child, ElementNode) and child.tag_name == "title":
                full_title = child.children[0].text
                for d in self.delimiters: #rozdělení title tagu pomocí oddělovačů
                    if d in full_title:
                        full_title = full_title.replace(d, "|")
                    full_title_list = full_title.split("|")
                    full_title = max(full_title_list, key=len).strip() #výběr nejdelší části title tagu
                return full_title #vrácení pravděpodobného nadpisu z title tagu

    def find_title_body(self, node): #hledání nadpisu pomocí h1 a h2 tagů v těle stránky, hledání v rodičovských uzlech hlavního obsahu
        if isinstance(node, ElementNode): #hledání h1 a h2 tagů v tomto uzlu
            if node.tag_name in ("h1", "h2"): #prohledání tohoto uzlu
                return self.get_text(node)

            for child in node.children: #rekurzivní prohledání potomků tohoto uzlu
                if isinstance(child, ElementNode):
                    result = self.find_title_body(child)
                    if result:
                        return result
        return None #vrácení None, pokud nenalezen žádný nadpis

    def match_titles(self, title_head, title_body): #porovnání pravděpodobných nadpisů pro vyloučení title_head tagů, které neodpovídají hlavnímu nadpisu
        if not title_head or title_body:
            return False
        h = title_head.lower().strip(" .!?:")
        b = title_body.lower().strip(" .!?:")
        if b in h or h in b:
            return True

    def heuristic(self):
        self.analyze(self.root) #nastavení parametrů pro hodnocení uzlů DOM
        article_body = self.find_best_node(self.root) #nalezení uzlu s nejvyšším skóre
        title_head = self.find_title_head(self.root) #nalezení pravděpodobného nadpisu pomocí title tagu
        title_body = self.find_title_body(article_body.parent_node) #nalezení pravděpodobného nadpisu v rodičovském tagu uzlu s nejvyšším skóre
        if title_body == None:
            title_body = self.find_title_body(article_body.parent_node.parent_node) #hledání pravděpodobného nadpisu o úroveň výš, pokud nebyl nalezen
        
        if title_body and self.match_titles(title_head, title_body): #ověření shody nadpisů
            self.final_text = self.get_text(article_body.parent_node) #určení hlavního obsahu jako rodičovský uzel uzlu s nejvyšším skóre, zahrnutý nadpis
        else:
            self.final_text = title_head + "\n" + self.get_text(article_body) #určení hlavního obsahu jako uzel s nejvyšším skóre, nadpis z little tagu
        return self.final_text #vrácení extrahovaného textu