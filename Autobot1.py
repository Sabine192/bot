from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import re

# Gebruik Service om de ChromeDriver op te zetten
service = Service(ChromeDriverManager().install())

# Zet de webbrowser op
driver = webdriver.Chrome(service=service)

# Maak het browservenster fullscreen
driver.maximize_window()

# De product URL en het maximum prijs
product_url = "https://www.bol.com/nl/nl/p/pokemon-boosterpack-scarlet-violet-booster-1-pakje-10-kaarten-tcg/9300000146583670/?bltgh=gGDvtPZyIjDvFm9V0MVAww.4_25.29.ProductTitle"
max_price = 20  # Nieuwe prijslimiet
desired_quantity = 4

# Ga naar de productpagina
driver.get(product_url)

# Wacht totdat de cookie pop-up verschijnt en klik op de "Accepteren" knop
wait = WebDriverWait(driver, 30)  # Verhoog wachttijd

# Probeer de 'Alles accepteren' knop te vinden met een meer robuuste methode
try:
    time.sleep(1)  # Kort wachten op pop-up
    cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "js-first-screen-accept-all-button")))
    cookie_button.click()
    print("Cookie pop-up geaccepteerd!")
except Exception as e:
    print("Cookie pop-up knop niet gevonden:", e)

# Wacht tot de 'Doorgaan' knop zichtbaar is (de tweede pop-up)
try:
    doorgaan_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Doorgaan')]")))
    doorgaan_button.click()
    print("Doorgaan pop-up geaccepteerd!")
except:
    print("Doorgaan pop-up knop niet gevonden.")

# Wacht even kort om zeker te zijn dat de pop-ups volledig zijn verwerkt
time.sleep(2)

# Functie om de beschikbaarheid van het product te controleren
def check_product_availability():
    """Controleer of het product beschikbaar is en onder de opgegeven prijs is."""
    print("Pagina wordt herladen...")
    driver.get(product_url)  # Dit herlaadt de pagina voor elke controle
    driver.refresh()
    print(f"De huidige url is: {driver.current_url}")
    wait = WebDriverWait(driver, 10)  # Verhoog wachttijd voor betrouwbaarheid

    # Wacht tot de knop "In winkelwagen" beschikbaar is
    try:
        add_to_cart_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "In winkelwagen")))
        print("Product beschikbaar!")

        # Zoek de dropdown voor hoeveelheid en selecteer de gewenste waarde
        try:
            quantity_dropdown = wait.until(EC.presence_of_element_located((By.ID, "quantityDropdown-buy-block")))  # Zoek de dropdown
            select = Select(quantity_dropdown)  # Maak een Select object voor de dropdown
            select.select_by_value(str(desired_quantity))  # Selecteer de hoeveelheid (bijvoorbeeld 1)
            print(f"Hoeveelheid ingesteld op {desired_quantity}.")
        except Exception as e:
            print(f"Fout bij het instellen van de hoeveelheid via dropdown: {e}")

        # Haal de prijs van het product op en controleer of het onder de opgegeven prijs is
        if get_product_price():  # Controleer of het product onder de opgegeven prijs is
            add_to_cart_button.click()  # Voeg het toe aan de winkelwagen
            print("Product toegevoegd aan winkelwagen!")
            
            # Wacht een korte tijd om de winkelwagen bij te werken
            time.sleep(3)  # Verhoog wachttijd indien nodig
            return True
        else:
            print("Product is te duur, niet toegevoegd aan winkelwagen.")
            return False  # Product is te duur, niet toevoegen aan winkelwagen

    except Exception as e:
        print("Product niet beschikbaar:", e)
        return False  # Het product is niet beschikbaar

# Functie om de prijs op te halen en te controleren of het onder de opgegeven prijs is
def get_product_price():
    """Haal de prijs van het product op en controleer of het onder de opgegeven prijs is."""
    try:
        # Zoek de tekst die de prijs bevat
        price_text = driver.find_element(By.CSS_SELECTOR, "span.srt[data-test='price-info-srt-text']").text
        
        # Gebruik reguliere expressies om de euro en cent te extraheren
        match = re.search(r"(\d+)\s+euro\s+en\s+(\d+)\s+cent", price_text)
        
        if match:
            euros = int(match.group(1))  # Haal de euro's op
            cents = int(match.group(2))  # Haal de centen op
            full_price = euros + cents / 100  # Zet de prijs om naar een float (bijv. 4 euro en 99 cent wordt 4.99)

            print(f"Prijs van het product: €{full_price}")

            # Vergelijk de prijs met de opgegeven limiet
            if full_price <= max_price:
                print(f"Product is onder de €{max_price}! Klaar om te kopen.")
                return True
            else:
                print(f"Product is te duur! De prijs is €{full_price}.")
                return False
        else:
            print("Fout: Kon de prijs niet extraheren uit de tekst.")
            return False

    except Exception as e:
        print("Fout bij het ophalen van de prijs:", e)
        return False

# Loop om de beschikbaarheid en prijs van het product continu te controleren
while True:
    if check_product_availability():  # Check of het product beschikbaar is en betaalbaar
        print("Product beschikbaar voor de juiste prijs!")
        break  # Stop de loop als het product is toegevoegd aan de winkelwagen
    else:
        print("Product niet beschikbaar of te duur, opnieuw proberen...")
        time.sleep(5)  # Wacht 5 seconden en probeer opnieuw

# Ga naar de winkelwagenpagina
driver.get("https://www.bol.com/nl/nl/basket/")

# Wacht even om te zorgen dat de winkelwagen geladen is
time.sleep(2)

def check_for_error_in_cart():
    """Controleer of er een foutmelding is bij het toevoegen van het product aan de winkelwagen."""
    try:
        # Verklein de wachttijd om sneller te reageren (bijv. 3 seconden)
        error_message = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'kan niet in de gewenste hoeveelheid worden geleverd')]")), timeout=2)
        if error_message:
            print("Foutmelding gevonden in winkelwagen")
            return True  # Fout gevonden, pagina moet opnieuw worden geladen
    except:
        print("Geen foutmelding gevonden in winkelwagen.")
    return False  # Geen foutmelding, alles is oké

def handle_error_and_retry():
    """Herlaad de productpagina en probeer het opnieuw als er een fout is."""
    error_found = check_for_error_in_cart()  # Controleer of er een fout is
    if error_found:
        print("Herlaad de pagina of probeer opnieuw")
        driver.get(product_url)  # Ga terug naar de productpagina
        time.sleep(2)  # Wacht een moment om te zorgen dat de pagina goed laadt
        return True  # We hebben opnieuw geprobeerd
    else:
        print("Geen fout gevonden, verder met het afrekenproces")
        return False  # Geen fout, alles is in orde

# Verander dit gedeelte van je code om de foutmelding op een andere manier af te handelen:
error_found = check_for_error_in_cart()  # Controleer of er een fout is
if error_found:
    # Verwerk de fout zoals gewenst, bijvoorbeeld door opnieuw te proberen of de pagina te herladen
    print("Herlaad de pagina of probeer opnieuw")
else:
    print("Geen fout gevonden, verder met het afrekenproces")

# Zoek en klik op de knop "Verder Bestellen"
try:
    verder_bestellen_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='mainContent']/wsp-basket-application/div[2]/div[2]/div/button")))
    verder_bestellen_button.click()
    print("Verder Bestellen geklikt, naar inlogpagina...")
except Exception as e:
    print("Fout bij het klikken op 'Verder Bestellen':", e)

# Wacht tot de inlogpagina geladen is
time.sleep(3)

# Nu gaan we inloggen (de pagina waar je normaal de inloggegevens invult)
try:
    # Vul het e-mailveld in
    email_input = wait.until(EC.presence_of_element_located((By.ID, "react-aria-1")))
    email_input.send_keys("nickverkaik@msn.com")
    
    # Vul het wachtwoordveld in
    password_input = wait.until(EC.presence_of_element_located((By.ID, "react-aria-5")))
    password_input.send_keys("qs8YAA")

    # Klik op de inlogknop
    login_submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Inloggen')]")
    login_submit_button.click()
    print("Ingelogd!")

except Exception as e:
    print("Fout bij het inloggen:", e)

# Nu gaan we verder met het afrekenproces
# Klik op de knop 'Afrekenen'
try:
    checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="paymentsuggestions"]/div[2]/div/div/ul/div[3]/div/p')))
    checkout_button.click()
    print("Afrekenpagina geopend!")
except Exception as e:
    print("Fout bij het openen van de afrekenpagina:", e)

# Wacht tot de afrekenpagina geladen is
time.sleep(3)

# Wacht totdat het betalingssuggestie-element zichtbaar is
try:
    payment_suggestion_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="paymentsuggestions"]/div[2]/div/div/ul/div[1]/div/p')))
    payment_suggestion_element.click()  # Klik op het betalingssuggestie-element
    print("Betalingsoptie geselecteerd!")
except Exception as e:
    print("Fout bij het vinden van het betalingssuggestie-element:", e)

# Voltooi het bestelproces (indien mogelijk)
try:
    bestel_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="executepayment"]/form/div/button')))
    bestel_button.click()
    print("Bestelling geplaatst!")
except Exception as e:
    print("Fout bij het plaatsen van bestelling:", e)

# Ga naar het iframe
try:
    iframe = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='radix-4']/div[2]/div[2]/div/div[2]/span/iframe")))
    driver.switch_to.frame(iframe)  # Schakel over naar het iframe
    print("Frame succesvol geladen!")
except Exception as e:
    print("Fout bij het laden van iframe:", e)

# Wacht tot het invoerveld voor de verificatiecode aanwezig is en vul de code in
try:
    # Zoek het invoerveld voor de verificatiecode
    verification_code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
    verification_code_input.send_keys("423")  # Vul je specifieke verificatiecode in
    print("Verificatiecode ingevuld!")
except Exception as e:
    print("Fout bij het invullen van de verificatiecode:", e)

# Schakel terug naar de hoofdpagina nadat de code is ingevuld
driver.switch_to.default_content()

# Wacht even om zeker te zijn dat de knop volledig geladen is
time.sleep(2)

try:
    betaal_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[span[contains(text(), 'Betalen')]]")))
    print("Betalingsknop gevonden!")
except Exception as e:
    print("Betalingsknop niet gevonden:", e)

# Zoek de "Betalen" knop en klik erop via de class naam of tekst
try:
    betaal_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Betalen')]]")))
    driver.execute_script("arguments[0].click();", betaal_button)
    print("Betaling voltooid!")
except Exception as e:
    print("Fout bij het klikken op de betaal knop:", e)

# Wacht enkele seconden om het proces goed af te handelen
time.sleep(5)

# Controleer of er een bevestigingspagina is
try:
    confirmation_message = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Bedankt voor je bestelling')]")))  # Bevestigingsbericht
    print("Bestelling succesvol geplaatst!")
except Exception as e:
    print("Bevestiging niet gevonden:", e)

 # Begin met het proces en herhaal als een bestelling is geplaatst
while True:
    if check_product_availability():  # Check of het product beschikbaar is en betaalbaar
        print("Product beschikbaar voor de juiste prijs!")
        if place_order():
            print("Bestelling voltooid, opnieuw beginnen met het controleren van het product.")
        else:
            print("Er was een probleem met de bestelling.")
    else:
        print("Product niet beschikbaar of te duur, opnieuw proberen...")
        time.sleep(5)  # Wacht 5 seconden en probeer opnieuw