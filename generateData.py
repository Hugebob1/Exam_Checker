from PIL import Image, ImageDraw, ImageFont
from random import choice, randint, random
import os
fonts = [
    "fonts/Caveat-VariableFont_wght.ttf",
    "fonts/GrapeNuts-Regular.ttf",
    "fonts/MsMadi-Regular.ttf",
    "fonts/QwitcherGrypen-Regular.ttf",
    "fonts/ShadowsIntoLight-Regular.ttf"
]

sheets_formats = {
    "A4_pion": (2480, 3508),
    "A4_poziom": (3508, 2480),
    "A5_pion": (1748, 2480)
}

baza_odpowiedzi = [
    # --- KRÓTKIE ---
    # --- NOWE DŁUGIE (Zamiast 10 krótkich) ---
    {"id": 1, "dlugosc": "dluga",
     "tekst": "Kwas deoksyrybonukleinowy, w skrócie DNA, to nośnik informacji genetycznej w komórce. Ma strukturę podwójnej helisy i składa się z nukleotydów. To w nim zapisane są wszystkie cechy organizmu, które dziedziczymy po naszych rodzicach."},
    {"id": 2, "dlugosc": "dluga",
     "tekst": "Rozbicie dzielnicowe w Polsce rozpoczęło się w 1138 roku po śmierci Bolesława Krzywoustego. Podzielił on państwo między swoich synów, aby zapobiec walkom o władze. Niestety, doprowadziło to do osłabienia kraju i utraty wielu terytoriów."},
    {"id": 3, "dlugosc": "dluga",
     "tekst": "Zjawisko pustynnienia polega na stopniowej degradacji gleb na obszarach suchych i półsuchych. Często jest wywołane przez zmiany klimatyczne oraz nadmierne wypasanie bydła. Prowadzi to do całkowitego zaniku roślinności i braku wody pitej."},
    # Celowy błąd: pitej -> pitnej
    {"id": 4, "dlugosc": "dluga",
     "tekst": "Pierwsza zasada dynamiki Newtona, zwana zasadą bezwładności, mówi, że jeśli na ciało nie działa żadna siła lub siły się równoważą, to ciało pozostaje w spoczynku. Jeśli było w ruchu, to porusza się dalej ruchem jednostajnym prostoliniowym."},
    {"id": 5, "dlugosc": "dluga",
     "tekst": "Kwasy to związki chemiczne zbudowane z atomu wodoru i reszty kwasowej. W roztworach wodnych ulegają dysocjacji jonowej, uwalniając kationy wodoru. Charakteryzują się kwaśnym smakiem i zmieniają kolor papierka lakmusowego na czerwony."},
    {"id": 6, "dlugosc": "dluga",
     "tekst": "Ekosystem to naturalny układ składający się z biocenozy, czyli wszystkich organizmów żywych na danym terenie, oraz biotopu, czyli środowiska nieożywionego. Elementy te nieustannie ze sobą oddziałują, tworząc stabilną i samoregulującą się całoś."},
    # Celowy błąd: całoś
    {"id": 7, "dlugosc": "dluga",
     "tekst": "Wielkie odkrycia geograficzne na przełomie XV i XVI wieku doprowadziły do odkrycia Ameryki przez Kolumba oraz opłynięcia Ziemi przez Magellana. Skutkiem tych wydarzeń był szybki rozwój handlu światowego, ale też zniszczenie cywilizacji prekolumbijskich."},
    {"id": 8, "dlugosc": "dluga",
     "tekst": "Atmosfera ziemska składa się z kilku warstw, z których najniższą i najważniejszą dla życia jest troposfera. To właśnie w niej zachodzą wszystkie zjawiska pogodowe i tworzą się chmury. Głównymi składnikami naszej atmosfery są azot i tlen."},
    {"id": 9, "dlugosc": "dluga",
     "tekst": "Prąd elektryczny to uporządkowany ruch ładunków elektrycznych. W metalach ładunkami tymi są swobodne elektrony. Aby prąd mógł płynąć w obwodzie, niezbędne jest źródło napięcia oraz zamknięta droga przepływu, czyli jakikolwiek przewodnik."},
    {"id": 10, "dlugosc": "dluga",
     "tekst": "Powieść Lalka Bolesława Prusa ukazuje panoramę dziewiętnastowiecznej Warszawy oraz konflikt między romantycznym idealizmem a pozytywistycznym rozsądkiem. Główny bohater, Stanisław Wokulski, próbuje zdobyć serce arystokratki, co doprowadza go do ruiny."},
    {"id": 11, "dlugosc": "krotka", "tekst": "Najdłuższą rzeką na świecie jest Nil albo Amazonka."},
    {"id": 12, "dlugosc": "krotka", "tekst": "Pan Tadeusz został napisany przez Adama Mickiewicza."},
    {"id": 13, "dlugosc": "krotka", "tekst": "Stolicą Niemiec jest Berlin."},
    {"id": 14, "dlugosc": "krotka", "tekst": "Tlen to gaz niezbędny do oddychania."},
    {"id": 15, "dlugosc": "krotka", "tekst": "Wielki Mur Chiński znajduje się w Azji."},
    {"id": 16, "dlugosc": "krotka", "tekst": "Słońce to gwiazda, wokół której krąży Ziemia."},
    {"id": 17, "dlugosc": "krotka", "tekst": "Australia to jednocześnie państwo i kontynent."},
    {"id": 18, "dlugosc": "krotka", "tekst": "Bitwa pod Grunwaldem odbyła się w 1410 roku."},

    # --- ŚREDNIE ---
    {"id": 19, "dlugosc": "srednia",
     "tekst": "Mitoza to proces podziału komórki somatycznej. W jej wyniku powstają dwie nowe komórki potomne, które mają identyczny materiał genetyczny jak komórka macierzysta."},
    {"id": 20, "dlugosc": "srednia",
     "tekst": "Klimat równikowy charakteryzuje się wysokimi temperaturami przez cały rok. Dodatkowo występują tam bardzo obfite deszcze zenitalne."},
    {"id": 21, "dlugosc": "srednia",
     "tekst": "Prawo Archimedesa mówi, że na ciało zanurzone w cieczy działa siła wyporu. Jest ona równa ciężarowi wypartej przez to ciało cieczy."},
    {"id": 22, "dlugosc": "srednia",
     "tekst": "Chrzest Polski odbył się w 966 roku za panowania Mieszka I. Decyzja ta wprowadziła Polskę w krąg kultury zachodnioeuropejskiej."},
    {"id": 23, "dlugosc": "srednia",
     "tekst": "Tęcza powstaje w wyniku zjawiska rozszczepienia światła białego. Promienie słońca załamują się w kroplach wody unoszących się w powietrzu po deszczu."},
    {"id": 24, "dlugosc": "srednia",
     "tekst": "Renesans, inaczej odrodzenie, to epoka w kulturze i sztuce europejskiej. Charakteryzowała się powrotem do ideałów antyku oraz humanizmem."},
    {"id": 25, "dlugosc": "srednia",
     "tekst": "Ptaki to zwierzęta stałocieplne, których ciało pokryte jest piórami. Większość z nich potrafi latać dzięki specjalnej budowie szkieletu, w którym występują kości pneumatyczne."},
    {"id": 26, "dlugosc": "srednia",
     "tekst": "Układ Słoneczny składa się ze Słońca i ośmiu planet. Ziemia jest trzecią planetą od Słońca, a największą z nich jest Jowisz."},
    {"id": 27, "dlugosc": "srednia",
     "tekst": "Rewolucja przemysłowa rozpoczęła się w Anglii w XVIII wieku. Jej symbolem stało się wynalezienie maszyny parowej przez Jamesa Watta."},
    {"id": 28, "dlugosc": "srednia",
     "tekst": "Grawitacja to zjawisko fizyczne polegające na przyciąganiu się ciał posiadających mase. To dzięki niej stoimy na ziemi i planety krążą wokół słońca."},
    # Literówka (mase/Słońca)
    {"id": 29, "dlugosc": "srednia",
     "tekst": "Ruch obrotowy Ziemi polega na jej obrocie wokół własnej osi. Trwa on 24 godziny i jego głównym skutkiem jest następstwo dnia i nocy."},
    {"id": 30, "dlugosc": "srednia",
     "tekst": "Wulkan to miejsce na powierzchni Ziemi, z którego wydobywa się lawa. Podczas erupcji uwalniane są także gazy i popioły wulkaniczne."},
    {"id": 31, "dlugosc": "srednia",
     "tekst": "Krwinki czerwone, czyli erytrocyty, odpowiadają za transport tlenu w organizmie. Zawierają hemoglobinę, która nadaje krwi czerwony kolor."},
    {"id": 32, "dlugosc": "srednia",
     "tekst": "ONZ to Organizacja Narodów Zjednoczonych. Jej głównym celem jest zapewnienie pokoju i bezpieczeństwa na świecie oraz współpraca między państwami."},
    {"id": 33, "dlugosc": "srednia",
     "tekst": "Pustynia to teren o bardzo małych opadach atmosferycznych. Roślinność jest tam bardzo uboga, a w dzień temperatury są ogromne, w nocy zaś mocno spadają."},
    {"id": 34, "dlugosc": "srednia",
     "tekst": "Dźwięk to fala akustyczna rozchodząca się w ośrodku sprężystym. Nie może on rozchodzić się w próżni, ponieważ potrzebuje cząsteczek do przenoszenia drgań."},

    # --- DŁUGIE ---
    {"id": 35, "dlugosc": "dluga",
     "tekst": "Przyczynami wybuchu I wojny światowej były liczne konflikty między mocarstwami europejskimi oraz walka o kolonie. Bezpośrednim pretekstem stał się zamach na arcyksięcia Franciszka Ferdynanda w Sarajewie w 1914 roku. W wyniku wojny upadły trzy wielkie cesarstwa: rosyjskie, niemieckie i austro-węgierskie."},
    {"id": 36, "dlugosc": "dluga",
     "tekst": "Układ krwionośny człowieka składa się z serca oraz naczyń krwionośnych: tętnic, żył i naczyń włosowatych. Serce działa jak pompa, która tłoczy krew do wszystkich komórek ciała. Krew dostarcza tlen i substancje odżywcze, a jednocześnie odbiera dwutlenek węgla i zbędne produkty przemiany materii, które są potem wydalane."},
    {"id": 37, "dlugosc": "dluga",
     "tekst": "Rzeźbotwórcza działalność lodowców górskich polega na niszczeniu i przenoszeniu materiału skalnego. Powstają w ten sposób charakterystyczne doliny U-kształtne oraz jeziora cyrkowe, takie jak Morskie Oko w Tatrach. Dodatkowo lodowiec zostawia po sobie ogromne wały kamieni, które nazywamy morenami."},
    {"id": 38, "dlugosc": "dluga",
     "tekst": "Demokracja to ustrój polityczny, w którym władza należy do obywateli. Mają oni prawo wyboru swoich przedstawicieli w wolnych i powszechnych wyborach. Podstawą państwa demokratycznego jest trójpodział władzy na ustawodawczą, wykonawczą i sądowniczą, co zapobiega nadużyciom i chroni prawa jednostki."},
    {"id": 39, "dlugosc": "dluga",
     "tekst": "Zjawisko globalnego ocieplenia jest spowodowane głównie działalnością człowieka i emisją gazów cieplarnianych do atmosfery. Gazy te, takie jak dwutlenek wengla i metan, zatrzymują ciepło promieniujące z powierzchni Ziemi. Skutkiem tego jest topnienie lodowców, podnoszenie się poziomu mórz i oceanów oraz coraz częstsze ekstremalne zjawiska pogodowe."},
    # Celowy błąd
    {"id": 40, "dlugosc": "dluga",
     "tekst": "W procesie trawienia układ pokarmowy rozkłada pokarm na proste związki chemiczne. Zaczyna się to już w jamie ustnej dzięki ślinie. Następnie pokarm trafia do żołądka, gdzie jest trawiony przez kwasy, a główny proces wchłaniania składników odżywczych do krwi odbywa się w jelicie cienkim dzięki kosmykom jelitowym."},
    {"id": 41, "dlugosc": "dluga",
     "tekst": "Starożytna Grecja nie była jednolitym państwem, lecz składała się z wielu niezależnych miast-państw, czyli polis. Najważniejszymi z nich były Ateny i Sparta. Grecy stworzyli fundamenty naszej cywilizacji, w tym teatr, igrzyska olimpijskie, filozofię oraz podwaliny ustroju demokratycznego."},
    {"id": 42, "dlugosc": "dluga",
     "tekst": "Elektrownie jądrowe produkują energię elektryczną wykorzystując reakcję rozszczepienia jąder uranu. Zaletą tego rozwiązania jest brak emisji szkodliwych pyłów i gazów cieplarnianych. Należy jednak pamiętać o problemie bezpiecznego składowania odpadów radioaktywnych oraz ryzyku awarii, chociaż dzisiejsze technologie są bardzo bezpieczne."},
    {"id": 43, "dlugosc": "dluga",
     "tekst": "Ewolucja to powolny proces zmian budowy organizmów żywych w czasie. Mechanizmem ewolucji jest dobór naturalny, opisany przez Karola Darwina. Przetrwają i rozmnażają się tylko te osobniki, które są najlepiej przystosowane do warunków środowiska, w którym żyją, przekazując swoje cechy potomstwu."},
    {"id": 44, "dlugosc": "dluga",
     "tekst": "Gospodarka wolnorynkowa opiera się na prywatnej własności i swobodzie konkurencji. O cenach towarów i usług decyduje prawo popytu i podaży na rynku. Państwo nie ingeruje bezpośrednio w gospodarkę, a przedsiębiorcy sami podejmują decyzje o tym, co i w jakich ilościach produkować, żeby osiągnąć zysk."},
    {"id": 45, "dlugosc": "dluga",
     "tekst": "Powstanie Warszawskie wybuchło 1 sierpnia 1944 roku i trwało 63 dni. Jego celem było wyzwolenie stolicy z rąk niemieckich przed wkroczeniem Armii Czerwonej. Mimo ogromnego bohaterstwa żołnierzy Armii Krajowej i ludności cywilnej, powstanie zakończyło się klęską i całkowitym zniszczeniem miasta."},
    {"id": 46, "dlugosc": "dluga",
     "tekst": "Funkcja kwadratowa opisana jest wzorem f(x) = ax^2 + bx + c. Wykresem tej funkcji jest parabola. Jeśli współczynnik a jest dodatni, ramiona paraboli skierowane są do góry, a jeśli jest ujemny, skierowane są w dół. Miejsca zerowe oblicza się za pomocą delty."},
    {"id": 47, "dlugosc": "dluga",
     "tekst": "Łańcuch pokarmowy pokazuje zależności pokarmowe między organizmami w ekosystemie. Zawsze zaczyna się od producentów, czyli roślin zielonych. Następnie są konsumenci I rzędu, czyli roślinożercy, a potem drapieżnicy. Na końcu łańcucha znajdują się reducenci, którzy rozkładają martwą materię organiczną."},
    {"id": 48, "dlugosc": "dluga",
     "tekst": "Ropa naftowa to surowiec energetyczny nazywany czarnym złotem. Wydobywa się ją ze złóż podziemnych. W rafineriach poddaje się ją procesowi destylacji, w wyniku którego uzyskuje się benzynę, olej napędowy, asfalt, a także tworzywa sztuczne. Jej spalanie jest jednak bardzo szkodliwe dla środowiska."},
    {"id": 49, "dlugosc": "dluga",
     "tekst": "Homer to najstarszy znany z imienia grecki poeta. Tradycja przypisuje mu autorstwo dwóch wielkich eposów starożytnych: Iliady, która opowiada o wojnie trojańskiej, oraz Odysei, opisującej dziesięcioletnią tułaczkę Odyseusza do rodzinnej Itaki. Jego dzieła miały ogromny wpływ na całą kulturę europejską."},
    {"id": 50, "dlugosc": "dluga",
     "tekst": "Tsunami to ogromne fale oceaniczne wywołane podwodnymi trzęsieniami ziemi lub wybuchami wulkanów. Na otwartym oceanie fala jest długa i niska, więc jest prawie niezauważalna dla statków. Kiedy jednak zbliża się do wybrzeża, woda spiętrza się, tworząc niszczycielską ścianę wody uderzającą w ląd."},
# --- EKSTRA DŁUGIE (Przypadki Skrajne) ---
    {"id": 51, "dlugosc": "extra_dluga", "tekst": "Fotosynteza to złożony proces biochemiczny, w którym rośliny, glony i niektóre bakterie przekształcają energię świetlną w energię chemiczną. Całość dzieli się na dwie główne fazy: fazę jasną, zachodzącą w granach chloroplastów, gdzie niezbędne jest światło do rozbicia cząsteczek wody i wydzielenia tlenu, oraz fazę ciemną, czyli cykl Calvina, zachodzącą w stromie. W fazie ciemnej roślina wykorzystuje dwutlenek węgla z atmosfery do produkcji glukozy. Proces ten jest absolutnym fundamentem życia na Ziemi, ponieważ nie tylko dostarcza tlenu niezbędnego do oddychania tlenowego dla większości organizmów, ale także stanowi podstawę wszystkich łańcuchów pokarmowych. Bez fotosyntezy obieg węgla w przyrodzie zostałby całkowicie zatrzymany, a ekosystemy uległyby załamaniu."},
    {"id": 52, "dlugosc": "extra_dluga", "tekst": "Wielka Rewolucja Francuska, która wybuchła w 1789 roku, była jednym z najważniejszych wydarzeń w nowożytnej historii Europy. Jej głównymi przyczynami były głębokie nierówności społeczne, podział na stany, z których tylko najbiedniejszy stan trzeci płacił podatki, oraz fatalna sytuacja gospodarcza kraju rządzongo przez Ludwika XVI. Symbolicznym początkiem rewolucji stało się zdobycie Bastylii 14 lipca. Wkrótce potem uchwalono Deklarację Praw Człowieka i Obywatela, która gwarantowała wolność, równość wobec prawa oraz nienaruszalność własności prywatnej. Mimo wzniosłych haseł, rewolucja szybko przerodziła się w krwawy terror, zwłaszcza pod rządami jakobinów. Ostatecznie doprowadziła ona do obalenia monarchii absolutnej, ścięcia króla i ustanowienia republiki, co na zawsze zmieniło oblicze polityczne całego kontynentu."},
    {"id": 53, "dlugosc": "extra_dluga", "tekst": "Teoria płyt tektonicznych zakłada, że zewnętrzna powłoka Ziemi, czyli litosfera, nie jest jednolitą skorupą, ale składa się z kilkunastu ogromnych, sztywnych płyt. Płyty te nieustannie przemieszczają się po plastycznej astenosferze dzięki prądom konwekcyjnym we wnętrzu planety. Tam, gdzie płyty oddalają się od siebie, powstają grzbiety śródoceaniczne, natomiast w strefach subdukcji, gdzie jedna płyta wsuwa się pod drugą, tworzą się głębokie rowy oceaniczne oraz wysokie łańcuchy górskie, takie jak Andy. To właśnie na granicach tych płyt najczęściej dochodzi do gwałtownych tszęsień ziemi oraz wybuchów wulkanów. Najbardziej znanym przykładem jest Pacyficzny Pierścień Ognia, gdzie aktywność sejsmiczna stanowi ogromne zagrożenie, wywołując niszczycielskie fale tsunami."},
    {"id": 54, "dlugosc": "extra_dluga", "tekst": "Pan Tadeusz, epopeja narodowa napisana przez Adama Mickiewicza na emigracji, to arcydzieło literatury polskiej epoki romantyzmu. Utwór ten nie tylko przedstawia barwny i wyidealizowany obraz życia polskiej szlachty na Litwie w przededniu wyprawy Napoleona na Rosję w 1812 roku, ale także niesie głębokie przesłanie patriotyczne. Główny wątek skupia się na sporze o zamek między zwaśnionymi rodami Horeszków i Sopliców, który ostatecznie kończy się zgodą. Niezwykle istotną postacią jest Jacek Soplica, ukrywający się pod habitem księdza Robaka. Jego wewnętrzna przemiana z porywczego warchoła w pokornego emisariusza jest symbolem drogi, jaką musiał przejść cały naród polski, aby odzyskać niepodległoś. Poemat kończy się radosnym i pełnym nadziei polonezem."},
    {"id": 55, "dlugosc": "extra_dluga", "tekst": "Podstawowe prawa termodynamiki to fundament współczesnej fizyki i inżynierii. Pierwsza zasada termodynamiki, będąca de facto zasadą zachowania energii, mówi, że energia w układzie izolowanym nie może zostać stworzona ani zniszczona, może jedynie zmieniać swoją formę, na przykład z energii cieplnej na pracę mechaniczną. Druga zasada wprowadza kluczowe pojęcie entropii, czyli miary nieuporządkowania układu. Zgodnie z nią, w procesach samorzutnych entropia wszechświata zawsze rośnie, co oznacza, że ciepło naturalnie przepływa tylko od ciała cieplejszego do zimniejszego, a nigdy odwrotnie bez użycia zewnętrznej pracy. To właśnie te prawa sprawiają, że zbudowanie perpetuum mobile, czyli maszyny pracującej w nieskończoność bez zasilania, jest fizycznie całkowicie niemożliwe."}
]
# uwaga na dwa zdjecia z extra dlugich chyba trzbeba bedzie je wyrzucic gdyz uciely tekst co bedzie nie miarodajne w testach

def add_grid_pattern(image, grid_spacing=50):

    draw = ImageDraw.Draw(image)
    width, height = image.size

    grid_color = (200, 210, 230)

    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=2)

    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=2)


def wrap_text(text, font, max_width):

    lines = []

    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        current_line = ""

        for word in words:

            test_line = f"{current_line} {word}".strip()

            width = font.getlength(test_line)

            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)
    return '\n'.join(lines)

def generate_text(txt, file_name):

    format_name, (width, height) = choice(list(sheets_formats.items()))
    sheet = Image.new('RGB', (width, height), color='white')
    if random() < 0.4:

        spacing = 40 if "A5" in format_name else 60
        add_grid_pattern(sheet, grid_spacing=spacing)
        print(f" -> Dodano wzór kratki (odstęp: {spacing}px)")

    pen = ImageDraw.Draw(sheet)

    font_path = choice(fonts)
    if format_name == "A5_pion":
        random_size = randint(50, 130)
    else:
        random_size = randint(80, 150)

    print(f"Generating: {file_name} | Format: {format_name} | Font size: {random_size}")

    try:

        font = ImageFont.truetype(font_path, size=random_size)
    except IOError:
        print("Błąd: Nie znaleziono pliku czcionki! Upewnij się, że plik .ttf jest w folderze.")
        return

    pen_type = choice(["czarny", "niebieski"])

    if pen_type == "czarny":
        shade = randint(0, 50)
        pen_color = (shade, shade, shade)
    else:
        R = randint(0, 30)
        G = randint(20, 70)
        B = randint(100, 220)
        pen_color = (R, G, B)

    x, y = randint(80, 150), randint(80, 150)
    right_margin = x + randint(50, 100)
    max_text_width = width - x - right_margin
    wrapped_txt = wrap_text(txt, font, max_text_width)

    pen.text((x, y), wrapped_txt, font=font, fill=pen_color)

    sheet.save(file_name)
    print(f"Gotowe! Wygenerowano plik: {file_name}")


folder = "dataset"
if not os.path.exists(folder):
    os.makedirs(folder)

print("Starting generation of 50 scans... This might take a few seconds.")

for answer in baza_odpowiedzi:
    file_id = str(answer["id"]).zfill(2)
    length = answer["dlugosc"]
    text = answer["tekst"]

    file_name = f"{folder}/scan_{file_id}_{length}.jpg"

    generate_text(text, file_name)

print(f"Done! There are 50 generated tests in the '{folder}' folder.")

