import random
import streamlit as st



#matematicke pomocne funkcije

def miller_rabin(n, k=40):
    """Miller-Rabin test prostosti
    Vrace True ako je broj vjerojatno prost
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
            if x == n - 1: #treba svi da budu jednaki -1 
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


# --- ČETIRI GLAVNA ZADATKA IZ PROJEKTA ---


def prim_num_find(k):
    """Pronalazi prost broj sa zadanim brojem k cifara"""
    while True:
        num = n_digit_random(k)
        #osiguravamo da je broj neparan
        if num % 2 == 0:
            num += 1
        if miller_rabin(num):
            return str(num)


def rsa_set(k):
    """Postavlja RSA sistem i vraca parametre kao stringove"""
    # 1. Pronadji p i q
    p_str = prim_num_find(k)
    q_str = prim_num_find(k)

    p = int(p_str)
    q = int(q_str)

    #Osigurajmo da p i q nisu isti brojevi
    while p == q:
        q_str = prim_num_find(k)
        q = int(q_str)

    # 2. Izracunaj N i Phi
    N = p * q
    phi = (p - 1) * (q - 1)

    # 3. Odaberi javni eksponent e
    # Standardni broj 65537 se najčešće koristi u praksi
    e = 65537
    if phi % e == 0:  # Rijedak slucaj kada 65537 nije relativno prost s phi
        e = 3
        while phi % e == 0:
            e += 2

    # 4. Izračunaj tajni eksponent d
    d = mod_inverse(e, phi)

    return str(p), str(q), str(N), str(e), str(d), str(phi)


def rsa_enc(message_str, N_str, e_str):
    """Enkripcija poruke pomocu javnog kljuca"""
    N = int(N_str)
    e = int(e_str)

    # Pretvaranje stringa u broj
    M = string_to_int(message_str)

    if M >= N:
        raise ValueError(
            "Poruka je predugačka za odabranu veličinu ključa (M >= N). Povećajte broj cifara k!"
        )

    # RSA formula: C = M^e mod N
    C = pow(M, e, N)
    return str(C)


def rsa_dec(ciphertext_str, N_str, d_str):
    """Dekripcija sifrata pomoću tajnog kljuca"""
    N = int(N_str)
    d = int(d_str)
    C = int(ciphertext_str)

    # RSA formula: M = C^d mod N
    M = pow(C, d, N)

    # Pretvaranje broja natrag u string
    return int_to_string(M)


# --- STREAMLIT (USER INTERFACE) ---

st.set_page_config(page_title="RSA Kriptosistem", page_icon="🔐", layout="wide")

st.title("🔐 Web aplikacija za RSA kriptosistem")
st.write(
    "Projektni zadatak iz Kriptografije - Implementacija asimetričnog šifrovanja tekstualnih poruka."
)

# Kreiranje tabova za bolju preglednost 
tab1, tab2, tab3 = st.tabs(
    ["⚙️ 1. Generisanje ključeva", "🔒 2. Enkripcija", "🔓 3. Dekripcija"]
)

# Spremamo generisane kljuceve u sesiju da ostanu vidljivi kroz tabove
if "p" not in st.session_state:
    st.session_state["p"] = ""
    st.session_state["q"] = ""
    st.session_state["N"] = ""
    st.session_state["e"] = ""
    st.session_state["d"] = ""
    st.session_state["phi"] = ""

# --- TAB 1: Generisanje KLJUČEVA ---
with tab1:
    st.header("Generisanje RSA Parametara")
    st.write(
        "Unesite željeni broj cifara $k$ kako bi pomoćni program pronašao proste brojeve i izračunao ključeve."
    )

    k_input = st.number_input(
        "Broj cifara za proste brojeve (k):",
        min_value=5,
        max_value=300,
        value=30,
        step=1,
    )

    if st.button("Pokreni `rsa_set`"):
        with st.spinner("Računam i tražim proste brojeve..."):
            p, q, N, e, d, phi = rsa_set(k_input)

            # Spremanje u stanje sesije
            st.session_state["p"] = p
            st.session_state["q"] = q
            st.session_state["N"] = N
            st.session_state["e"] = e
            st.session_state["d"] = d
            st.session_state["phi"] = phi

        st.success("Sistem uspješno postavljen!")

    # Prikaz rezultata u strukturiranom obliku
    if st.session_state["N"]:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Privatni parametri (Tajni)")
            st.text_area("Prost broj p", st.session_state["p"], disabled=True)
            st.text_area("Prost broj q", st.session_state["q"], disabled=True)
            st.text_area(
                "Eulerova funkcija φ(N)", st.session_state["phi"], disabled=True
            )
            st.text_input(
                "Tajni eksponent (d) - Tvoj ključ",
                st.session_state["d"],
                disabled=True,
            )

        with col2:
            st.subheader("Javni parametri (Sve dostupno)")
            st.text_area("Modul (N = p * q)", st.session_state["N"], disabled=True)
            st.text_input(
                "Javni eksponent (e)", st.session_state["e"], disabled=True
            )

            st.info(
                "💡 Parametri su automatski prebačeni u tabove za Enkripciju i Dekripciju."
            )


# --- TAB 2: ENKRIPCIJA ---
with tab2:
    st.header("Šifrovanje poruke (`rsa_enc`)")

    enc_message = st.text_area(
        "Unesite tekstualnu poruku (string):",
        placeholder="Napišite tajnu poruku ovdje...",
    )

    col1, col2 = st.columns(2)
    with col1:
        enc_N = st.text_area("Modul N (iz javnog ključa):", st.session_state["N"])
    with col2:
        enc_e = st.text_input("Eksponent e (iz javnog ključa):", st.session_state["e"])

    if st.button("Šifruj poruku"):
        if not enc_message or not enc_N or not enc_e:
            st.warning("Molimo popunite sva polja ili generišite ključeve u prvom tabu.")
        else:
            try:
                sifra = rsa_enc(enc_message, enc_N, enc_e)
                st.subheader("Rezultat enkripcije (Šifrat):")
                st.code(sifra, language="text")
                st.caption(
                    "Ovaj niz brojeva možete sigurno poslati preko bilo kojeg kanala."
                )
            except Exception as ex:
                st.error(f"Greška: {ex}")


# --- TAB 3: DEKRIPCIJA ---
with tab3:
    st.header("Dešifrovanje poruke (`rsa_dec`)")

    dec_ciphertext = st.text_area(
        "Unesite šifrovani tekst (brojčani niz):",
        placeholder="Zalijepite generisani šifrat ovdje...",
    )

    col1, col2 = st.columns(2)
    with col1:
        dec_N = st.text_area("Modul N:", st.session_state["N"])
    with col2:
        dec_d = st.text_input("Tajni eksponent d:", st.session_state["d"])

    if st.button("Dešifruj poruku"):
        if not dec_ciphertext or not dec_N or not dec_d:
            st.warning("Molimo popunite sva polja kako biste dešifrovali poruku.")
        else:
            try:
                originalni_tekst = rsa_dec(dec_ciphertext, dec_N, dec_d)
                st.subheader("Originalna poruka:")
                st.success(originalni_tekst)
            except Exception as ex:
                st.error(
                    f"Neuspješna dekripcija. Provjerite unesene podatke. Detalji greške: {ex}"
                )