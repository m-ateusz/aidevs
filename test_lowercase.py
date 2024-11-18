from aidevs import send_task

def main():
    # Answer dictionary with categorized files
    answer = {'2024-11-12_report-04-sektor_B2.txt': 'patrol, zachodni sektor, bezpieczeństwo, brak anomalii, komunikacja czysta, monitoring, teren', 
              '2024-11-12_report-06-sektor_C2.txt': 'sektor północno-zachodni, skanery temperatury, skanery ruchu, brak wykrycia, jednostka operacyjna, patrol', 
              '2024-11-12_report-07-sektor_C4.txt': 'Czujniki dźwięku, javascript, c4, sektor_c4, ultradźwiękowy sygnał, nadajnik, zielone krzaki, las, analiza obiektu, odciski palców, Barbara Zawadzka, dział śledczy, obszar zabezpieczony, patrol, incydenty', 
              '2024-11-12_report-03-sektor_A3.txt': 'patrol, monitorowanie, czujniki, życie organiczne, stan patrolu, brak rezultatów', 
              '2024-11-12_report-05-sektor_C1.txt': 'monitorowanie, sensor dźwiękowy, detektory ruchu, brak aktywności organicznej, brak aktywności technologicznej, patrol, bezpieczeństwo', 
              '2024-11-12_report-02-sektor_A3.txt': 'patrol nocny, monitoring, aktywność organiczna, aktywność mechaniczna, obszar, peryferie obiektu', 
              '2024-11-12_report-00-sektor_C4.txt': 'Aleksander Ragowski, nauczyciel, programista, Java, detekcja biometryczna, jednostka organiczna,  północne skrzydło, fabryka, patrol, kontrola.', 
              '2024-11-12_report-01-sektor_A1.txt': 'ruch organiczny, zwierzyna leśna, fałszywy alarm, obszar bezpieczny, patrol, detekcja, monitorowanie, analiza wizualna, analiza sensoryczna', 
              '2024-11-12_report-08-sektor_A1.txt': 'monitoring, obszar patrolowy, bezruch, czujniki, jaka aktywność, obserwacja, wyznaczone wytyczne, sektor bezpieczeństwa', 
              '2024-11-12_report-09-sektor_C2.txt': 'patrol, peryferie, zachodni, czujniki, brak sygnałów, obszar, anomalie, monitoring, bezpieczeństwo'}

    # Send the answer to the task endpoint
    send_task("dokumenty", answer)

if __name__ == "__main__":
    main() 