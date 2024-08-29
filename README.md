# Annotációt (Is) Segítő Alkalmazás

## Használat

Függőségek telepítése:
`pip install requirements.txt`

Modell beszerzése:
`git clone https://huggingface.co/huspacy/hu_core_news_trf`

Az automatikus annotáló futtatása:
    1. Hozzuk létre azt a könyvtárat amely majd a nyers szövegfájlokat tartalmazza.
       Pl. `data` néven.
    2. Futtasuk a programot paraméterül ezen könyvtár nevét megadva:
       `python main.py data`
    3. A kimenet az `output` könyvtárba fog kerülni. Konvertáljuk ezt html fájlokká.
       `python tools/annot_to_html.py output/`
    4. Ellenőrizzük a kimenetet a böngészőből megnyitva a html fájlokat.       
