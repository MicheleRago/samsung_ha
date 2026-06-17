# Samsung Custom Appliances for Home Assistant

Questa integrazione personalizzata per Home Assistant permette di controllare e monitorare i tuoi elettrodomestici Samsung (Lavastoviglie, Lavasciuga, Forno, Frigorifero) aggirando le limitazioni dell'integrazione ufficiale SmartThings.

Viene utilizzata una comunicazione REST API diretta verso i server SmartThings per esporre funzionalità avanzate come:
- Selezione del programma (Lavastoviglie, Lavasciuga)
- Controllo dell'accensione/spegnimento e Avvio/Pausa/Stop
- Monitoraggio delle temperature
- Lettura dinamica delle *capabilities* supportate dal tuo modello specifico.

## Installazione tramite HACS

Questa repository è compatibile con [HACS](https://hacs.xyz/).

1. Apri **HACS** in Home Assistant.
2. Clicca su **Integrazioni**.
3. Clicca sui 3 pallini in alto a destra e seleziona **Repository personalizzati**.
4. Incolla l'URL di questa repository GitHub.
5. Seleziona **Integrazione** come categoria e clicca su Aggiungi.
6. Una volta aggiunta, cerca "Samsung Custom Appliances" e installala.
7. **Riavvia Home Assistant**.

## Configurazione

Per usare l'integrazione, ti servirà un **Personal Access Token (PAT)** di SmartThings.

### Come generare il Token:
1. Vai sul [Portale SmartThings per i Token](https://account.smartthings.com/tokens).
2. Accedi con il tuo account Samsung.
3. Clicca su **Generate new token**.
4. Assegna un nome (es. "Home Assistant Custom").
5. Spunta le caselle sotto la voce **Devices** (`r:devices:*` e `x:devices:*`).
6. Clicca su **Generate token** e copia la chiave. **Attenzione: viene mostrata una volta sola.**

### Aggiunta a Home Assistant
1. Vai su **Impostazioni > Dispositivi e Servizi**.
2. Clicca su **Aggiungi Integrazione**.
3. Cerca "Samsung Custom Appliances".
4. Incolla il tuo Personal Access Token nel campo richiesto.
5. L'integrazione troverà automaticamente tutti gli elettrodomestici compatibili sul tuo account e li configurerà.

## Attenzione (Modalità Remota)
Per poter avviare la lavastoviglie o la lavatrice tramite Home Assistant (es. tasto *Run*), **devi ricordarti di attivare fisicamente il pulsante "Smart Control" (o Remote Control)** sul pannello dell'elettrodomestico quando lo carichi. Per motivi di sicurezza, la maggior parte degli elettrodomestici Samsung disabilita l'avvio remoto ogni volta che lo sportello viene aperto. L'integrazione espone un sensore `Remote Control` in modo che tu possa verificare lo stato della modalità remota da Home Assistant.
