#pip install -r requirements.txt
import streamlit as st

from htmlExtract import HtmlExtract
from tokenizer import Tokenizer
from domBuilder import DOMbuilder
from heuristics import Heuristic
from transcript import Transcript

@st.cache_data
def process_to_braille(url): #Logická část programu
    #1 - načtení html kódu
    extractor = HtmlExtract(url)
    html_code = extractor.extract()

    #2 - tokenizace textu
    tokenizer = Tokenizer(html_code)
    tokens = tokenizer.tokenize()
    
    #3 - tvorba DOM stromu
    builder = DOMbuilder(tokens)
    DOM = builder.built()

    #4 - heruistiky
    heuristic = Heuristic(DOM)
    text = heuristic.heuristic()
    
    #5 - přepis do Braille
    transcript = Transcript(text) 
    result = transcript.to_braille()
    visualisation = transcript.visualize(result)

    return result, visualisation

def main(): #Uživatelské rozhraní
    st.title("Převodník webové stránky do Braillova písma")
    url_manual = "https://www.osel.cz/14557-neandrtalci-a-praveci-homo-sapiens-kdo-s-kym.html#google_vignette"
    url = st.text_area("Vložte url:") #streamlit input
    if url:
        result, visualisation = process_to_braille(url)
        st.subheader("Náhled:") #visualizace braillu na webu
        st.code(visualisation)

        st.download_button("Stáhnout .brf:", data = result, file_name = "export.brf") #tlačítko pro stažení souboru

if __name__ == "__main__": #spuštění programu
    main()