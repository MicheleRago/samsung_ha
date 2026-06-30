# Samsung Custom Appliances for Home Assistant

Integrazione custom per controllare elettrodomestici Samsung tramite SmartThings REST API da Home Assistant.

Supporta entità dinamiche per lavastoviglie, lavatrice/lavasciuga, forno e frigorifero in base alle capability esposte dal singolo dispositivo.

## Funzionalità

- Accensione, spegnimento e comandi `Run`, `Pause`, `Stop`.
- Selezione programmi per lavastoviglie, lavatrice e asciugatrice.
- Controlli forno per modalità, temperatura, tempo cottura, start/pause/stop e lampada.
- Sensori stato macchina, stato lavoro, tempi residui/completamento, temperatura e remoto.
- Switch opzioni dove supportati: mezzo carico, speed booster, sanitize, auto open door, power cool/freeze e child lock.

## Installazione

Questa repository è compatibile con HACS come integrazione custom.

1. Apri HACS in Home Assistant.
2. Vai in **Integrazioni**.
3. Apri **Repository personalizzati**.
4. Incolla l'URL della repository.
5. Seleziona **Integrazione** come categoria.
6. Installa **Samsung Custom Appliances**.
7. Riavvia Home Assistant.

## Configurazione OAuth

Il config flow usa OAuth SmartThings, non un Personal Access Token.

1. Crea un'app OAuth SmartThings con scope `r:devices:*` e `x:devices:*`.
2. Imposta il redirect URI su `https://google.com`.
3. In Home Assistant vai in **Impostazioni > Dispositivi e servizi > Aggiungi integrazione**.
4. Cerca **Samsung Custom Appliances**.
5. Inserisci `Client ID` e `Client Secret`.
6. Apri il link di autorizzazione mostrato dal flow.
7. Dopo il redirect su Google, copia l'intero URL del browser e incollalo nel campo richiesto.

L'integrazione salva access token e refresh token nella config entry e aggiorna i token automaticamente quando SmartThings risponde con `401`.

## Card Lovelace

Le card restano in cartelle top-level per non rompere i percorsi usati nelle risorse Lovelace.

- `samsung-oven-card/samsung-oven-card.js`
- `samsung-dishwasher-card/samsung-dishwasher-card.js`
- `samsung-washer-card/samsung-washer-card.js`
- `samsung-fridge-card/samsung-fridge-card.js`

Ogni cartella contiene un README con YAML di esempio.

## Note Forno

Per il modello forno usato durante lo sviluppo sono esposte solo queste modalità:

- `Convezione` -> `Bake`
- `Ventola convenzionale` -> `FanConventional`
- `Grill Grande` -> `Broil`
- `Grill ventilato` -> `ConvectionBroil`
- `Riscaldamento superiore+convezione` -> `ConvectionRoast`
- `Riscaldamento inferiore+convezione` -> `ConvectionBake`
- `Cottura intensiva` -> `SlimStrong`
- `Rosolatura` -> `BottomHeat`

`FanConventional` usa il comando SmartThings batch moderno (`setOvenMode`, `setOvenSetpoint`, `setOperationTime`, `start`). Le altre modalità usano il payload legacy `ovenOperatingState/start` perché su questo forno risultano più affidabili.

## Struttura Codice

- `custom_components/samsung_custom/api.py`: client SmartThings REST, refresh OAuth e logging payload.
- `custom_components/samsung_custom/coordinator.py`: aggiornamento periodico dati dispositivi.
- `custom_components/samsung_custom/entity.py`: helper condivisi per componenti, stati, device info e refresh post-comando.
- `custom_components/samsung_custom/oven.py`: logica specifica forno e costruzione payload start.
- `custom_components/samsung_custom/{sensor,binary_sensor,switch,select,number,button,light}.py`: platform Home Assistant.

## Modalità Remota

Per avviare lavastoviglie, lavatrice o forno da Home Assistant, SmartThings richiede spesso l'abilitazione fisica di **Smart Control** o **Remote Control** sul pannello del dispositivo. Dopo l'apertura dello sportello, molti elettrodomestici Samsung disabilitano l'avvio remoto per sicurezza.
