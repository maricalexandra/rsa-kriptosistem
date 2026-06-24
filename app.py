import random
from math import gcd
import streamlit as st



#matematicke pomocne funkcije

def miller_rabin(n, k=40):
    """Miller-Rabin test prostosti
    Vraca True ako je broj vjerojatno prost
    """
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False

    #zapisemo n-1 kao 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    #svjedoci prostosti
    for _ in range(k): #provjerimo 40 baza
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: #treba jedan da je jednak -1 
                break
        else:
            return False
    return True


#generisanje random broja 
def n_digit_random(digits):
    lower = 10 ** (digits - 1) #donja granica
    upper = (10**digits) - 1 #gordnja granica
    return random.randint(lower, upper)


def extended_gcd(a, b):
    """prosireni Euklidov algoritam za racunanje modularnog inverza"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def mod_inverse(e, phi):
    """racuna tajni eksponent d takav da je (d * e) % phi == 1"""
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1:
        return None  #modularni inverz ne postoji
    else:
        return x % phi


def string_to_int(text_string):
    """Pretvara string u jedan veliki cijeli broj preko ASCII vrijednosti bita"""
    hex_str = text_string.encode("utf-8").hex()
    return int(hex_str, 16)


def int_to_string(large_int):
    """pretvara veliki cijeli broj nazad u originalni string"""
    try:
        hex_str = hex(large_int)[2:]
        if len(hex_str) % 2 != 0:
            hex_str = "0" + hex_str
        return bytes.fromhex(hex_str).decode("utf-8")
    except Exception:
        return "[greska pri dekodiranju teksta - provjerite kljuceve]"




def prim_num_find(k):
    """Pronalazi prost broj sa zadanim brojem k cifara"""
    while True:
        num = n_digit_random(k)
        #osiguravamo da je broj neparan
        if num % 2 == 0:
            num += 1
        if miller_rabin(num):
            return str(num)


def rsa_set(k, e=65537):
    """Postavlja RSA sistem i vraća parametre kao stringove"""

    p_str = prim_num_find(k)
    q_str = prim_num_find(k)

    p = int(p_str)
    q = int(q_str)

    #  p i q nisu isti
    while p == q:
        q_str = prim_num_find(k)
        q = int(q_str)

    N = p * q
    phi = (p - 1) * (q - 1)

    # da li je e dozvoljen
    if gcd(e, phi) != 1:
        raise ValueError(
            f"Izabrani eksponent e = {e} nije relativno prost sa φ(N)."
        )

    d = mod_inverse(e, phi)

    return (
        str(p),
        str(q),
        str(N),
        str(e),
        str(d),
        str(phi)
)

def rsa_enc_full(message_str, N_str, e_str):

    N = int(N_str)
    e = int(e_str)

    M = string_to_int(message_str)

    if M >= N:
        raise ValueError(
            "Poruka je predugačka za izabrani ključ."
        )

    return str(pow(M, e, N))

def rsa_dec_full(ciphertext_str, N_str, d_str):

    N = int(N_str)
    d = int(d_str)

    C = int(ciphertext_str)

    M = pow(C, d, N)

    return int_to_string(M)



def rsa_enc_chars(message_str, N_str, e_str):
    """Enkripcija poruke pomoću javnog ključa"""

    N = int(N_str)
    e = int(e_str)

    encrypted_blocks = []

    for ch in message_str:

        m = ord(ch)

        if m >= N:
            raise ValueError(
                "RSA ključ je premali. Povećajte broj cifara pri generisanju ključeva."
            )

        c = pow(m, e, N)

        encrypted_blocks.append(str(c))

    return " ".join(encrypted_blocks)


def rsa_dec_chars(ciphertext_str, N_str, d_str):
    """Dekripcija šifrata pomoću privatnog ključa"""

    N = int(N_str)
    d = int(d_str)

    decrypted_text = ""

    encrypted_blocks = ciphertext_str.split()

    for block in encrypted_blocks:

        c = int(block)

        m = pow(c, d, N)

        decrypted_text += chr(m)

    return decrypted_text



# --- STREAMLIT (USER INTERFACE) ---


st.set_page_config(
    page_title="RSA Cryptosystem",
    page_icon="🔐",
    layout="wide"
)

# SESSION STATE
for key in ["p", "q", "N", "e", "d", "phi"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# CSS

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.stApp{
background:
radial-gradient(circle at 15% 20%, rgba(59,130,246,.25), transparent 30%),
radial-gradient(circle at 85% 80%, rgba(139,92,246,.25), transparent 30%),
#020617;
}

.hero{
    background:
    radial-gradient(circle at top left,#2563eb,transparent 40%),
    radial-gradient(circle at bottom right,#7c3aed,transparent 40%),
    #0f172a;

    padding:60px;
    border-radius:30px;
    text-align:center;
    color:white;
    margin-bottom:30px;

    border:1px solid rgba(255,255,255,.08);

    box-shadow:
    0 30px 80px rgba(37,99,235,.25);
}

.metric-card{
    background:rgba(255,255,255,.06);
    backdrop-filter:blur(20px);
    border:1px solid rgba(255,255,255,.10);
    border-radius:24px;
    padding:24px;
    box-shadow:
    0 10px 40px rgba(0,0,0,.40),
    inset 0 1px 0 rgba(255,255,255,.08);
}

.block-container{
    padding-top:1.5rem;
    max-width:1400px;
}

div.stButton > button{
    width:100%;
    height:56px;
    border:none;
    border-radius:16px;
    font-weight:700;
    font-size:15px;
    background:linear-gradient(135deg,#2563eb,#7c3aed);
    color:white;
    box-shadow:0 10px 30px rgba(99,102,241,.35);
}

div.stButton > button:hover{
    transform:translateY(-3px);
    transition:.25s;
}

div[data-testid="stTextArea"],
div[data-testid="stTextInput"]{
    background:rgba(255,255,255,.04);
    border-radius:18px;
}

h1,h2,h3,label,p{
    color:white !important;
}

[data-testid="stSidebar"]{
    background:#0b1220;
}
            
div[data-testid="stDownloadButton"] > button{
    width:100%;
    height:56px;
    border:none;
    border-radius:16px;
    font-weight:700;
    font-size:15px;

    background:linear-gradient(135deg,#2563eb,#7c3aed);
    color:white !important;

    box-shadow:0 10px 30px rgba(99,102,241,.35);
}

div[data-testid="stDownloadButton"] > button:hover{
    transform:translateY(-3px);
    transition:.25s;
}

      
          

</style>
""", unsafe_allow_html=True)


# HERO
st.markdown("""
<div class="hero">
    <h1>RSA kriptosistem </h1>
    <p>Implementacija asimetrične kriptografije za sigurno šifrovanje poruka</p>
</div>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ Generisanje parametara",
    "🔒 Enkripcija",
    "🔓 Dekripcija",
    "📊 RSA Parametri"
])

# TAB 1 - GENERISANJE

with tab1:

    st.subheader("Generisanje RSA ključeva")

    st.info("""
    Ovaj dio aplikacije služi za generisanje RSA kriptografskog sistema.

    Program automatski pronalazi dva velika prosta broja p i q,
    a zatim izračunava sve parametre potrebne za RSA enkripciju
    i dekripciju.

    Koraci:
    1. Unesite željeni broj cifara prostih brojeva.
    2. Kliknite na dugme „Generiši RSA ključeve“.
    3. Program računa p, q, N, φ(N), e i d.
    4. Generisani parametri mogu se koristiti za šifrovanje i dešifrovanje poruka.

    Napomena:
    Veći broj cifara povećava bezbjednost sistema, ali produžava vrijeme generisanja ključeva.
    """)


    k_input = st.number_input(
        "Broj cifara prostih brojeva p i q",
        min_value=5,
        max_value=300,
        value=30
    )

    if st.button("Generiši RSA ključeve"):

        with st.spinner("Generisanje RSA ključeva u toku..."):

            p, q, N, e, d, phi = rsa_set(k_input)

            st.session_state["p"] = p
            st.session_state["q"] = q
            st.session_state["N"] = N
            st.session_state["e"] = e
            st.session_state["d"] = d
            st.session_state["phi"] = phi

    if st.session_state["N"]:

        bits = int(st.session_state["N"]).bit_length()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Cifara u p", len(st.session_state["p"]))
        c2.metric("Cifara u q", len(st.session_state["q"]))
        c3.metric("Cifara u N", len(st.session_state["N"]))
        c4.metric("Jačina ključa", f"{bits} bita")


# TAB 2 - ENKRIPCIJA

with tab2:

    st.subheader("Enkripcija poruke")

    st.info("""
    Ovaj dio aplikacije služi za RSA enkripciju poruka.

    Koraci:
    1. Unesite poruku direktno ili učitajte tekstualnu datoteku.
    2. Izaberite način enkripcije.
    3. Program koristi javni RSA ključ generisan u tabu
    „Generisanje parametara“.
    4. Kliknite na dugme „Enkriptuj poruku“.
    5. Dobijeni šifrat možete sačuvati u datoteku.

    Podržana su dva načina rada: cijela poruka kao jedan broj i karakter po karakter.
    """)

    mode = st.radio(
        "Način RSA enkripcije",
        [
            "Cijela poruka",
            "Karakter po karakter"
        ]
    )

    message = st.text_area(
        "Tekst za enkripciju",
        height=250,
        placeholder="Unesite poruku...",
        key="message_input"
    )

    uploaded_file = st.file_uploader(
        "Ili učitajte tekstualnu datoteku",
        type=["txt"]
    )

    if uploaded_file is not None:

        try:

            file_content = uploaded_file.read().decode("utf-8")

            st.success("Datoteka je uspješno učitana.")

            st.text_area(
                "Sadržaj učitane datoteke",
                value=file_content,
                height=150,
                disabled=True,
                key="loaded_file_content"
            )

            message = file_content

        except Exception:

            st.error(
                "Greška prilikom učitavanja datoteke."
            )

    if st.session_state["N"]:

        st.text_area(
            "Javni modul N",
            value=st.session_state["N"],
            height=120,
            disabled=True,
            key="public_N_view"
        )

        st.text_input(
            "Javni eksponent e",
            value=st.session_state["e"],
            disabled=True,
            key="public_e_view"
        )

    if st.button("Enkriptuj poruku"):

        if not st.session_state["N"]:

            st.warning(
                "Najprije generišite RSA parametre."
            )

        elif not message:

            st.warning(
                "Unesite poruku ili učitajte datoteku."
            )

        else:

            try:

                if mode == "Cijela poruka":

                    cipher = rsa_enc_full(
                        message,
                        st.session_state["N"],
                        st.session_state["e"]
                    )

                else:

                    cipher = rsa_enc_chars(
                        message,
                        st.session_state["N"],
                        st.session_state["e"]
                    )

                st.success(
                    "Enkripcija je uspješno izvršena."
                )

                st.code(
                    cipher,
                    language="text"
                )

                st.download_button(
                    "Sačuvaj šifrat",
                    cipher,
                    file_name="sifrat.txt",
                    mime="text/plain"
                )

            except Exception as ex:

                st.error(str(ex))


# TAB 3 - DEKRIPCIJA
with tab3:

    st.subheader("Dekripcija poruke")

    st.info("""
    Ovaj dio aplikacije služi za RSA dekripciju šifrata.

    Koraci:
    1. Unesite šifrat direktno ili učitajte tekstualnu datoteku.
    2. Izaberite način dekripcije koji odgovara načinu korišćenom pri enkripciji.
    3. Program koristi privatni RSA ključ generisan u tabu
    „Generisanje parametara“.
    4. Kliknite na dugme „Dekriptuj poruku“.
    5. Originalna poruka će biti prikazana na ekranu.
    Podržana su dva načina rada: cijela poruka kao jedan broj i karakter po karakter.
            
    Napomena:
    Za dekripciju se koristi privatni ključ (N, d).
    """)

    mode = st.radio(
        "Način RSA dekripcije",
        [
            "Cijela poruka",
            "Karakter po karakter"
        ],
        key="decrypt_mode"
    )

    ciphertext = st.text_area(
        "Šifrat",
        height=250,
        placeholder="Unesite ili nalijepite šifrat...",
        key="ciphertext_input"
    )

    uploaded_cipher = st.file_uploader(
        "Ili učitajte datoteku sa šifratom",
        type=["txt"],
        key="cipher_file"
    )

    if uploaded_cipher is not None:

        try:

            cipher_content = uploaded_cipher.read().decode("utf-8")

            st.success(
                "Datoteka sa šifratom je uspješno učitana."
            )

            st.text_area(
                "Sadržaj učitane datoteke",
                value=cipher_content,
                height=150,
                disabled=True,
                key="loaded_cipher_content"
            )

            ciphertext = cipher_content

        except Exception:

            st.error(
                "Greška prilikom učitavanja datoteke."
            )

    if st.session_state["N"]:

        st.text_area(
            "Modul N",
            value=st.session_state["N"],
            height=120,
            disabled=True,
            key="private_N_view"
        )

        st.text_area(
            "Privatni eksponent d",
            value=st.session_state["d"],
            height=120,
            disabled=True,
            key="private_d_view"
        )

    if st.button("Dekriptuj poruku"):

        if not st.session_state["N"]:

            st.warning(
                "Najprije generišite RSA parametre."
            )

        elif not ciphertext:

            st.warning(
                "Unesite šifrat ili učitajte datoteku."
            )

        else:

            try:

                if mode == "Cijela poruka":

                    text = rsa_dec_full(
                        ciphertext,
                        st.session_state["N"],
                        st.session_state["d"]
                    )

                else:

                    text = rsa_dec_chars(
                        ciphertext,
                        st.session_state["N"],
                        st.session_state["d"]
                    )

                st.success(
                    "Dekripcija je uspješno izvršena."
                )

                st.text_area(
                    "Originalna poruka",
                    value=text,
                    height=200,
                    key="decrypted_text",
                    disabled=True
                )

                st.download_button(
                    "Sačuvaj dekriptovanu poruku",
                    text,
                    file_name="dekriptovana_poruka.txt",
                    mime="text/plain"
                )

            except Exception as ex:

                st.error(str(ex))


# TAB 4 - PARAMETRI

with tab4:

    if st.session_state["N"]:

        col1, col2 = st.columns(2)

        with col1:

            st.text_area(
                "Prime Number p",
                value=st.session_state["p"],
                height=150,
                disabled=True
            )

            st.text_area(
                "Prime Number q",
                st.session_state["q"],
                height=150,
                disabled=True
            )

            st.text_area(
                "φ(N)",
                st.session_state["phi"],
                height=150,
                disabled=True
            )

        with col2:

            st.text_area(
                "Modulus N",
                st.session_state["N"],
                height=150,
                disabled=True
            )

            st.text_input(
                "Public exponent e",
                st.session_state["e"],
                disabled=True
            )

            st.text_area(
                "Private exponent d",
                st.session_state["d"],
                height=150,
                disabled=True
            )