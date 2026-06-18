# Samsung Fridge Custom Card

Una card moderna ed elegante per controllare il tuo frigorifero Samsung in Home Assistant, basata sull'estetica della `samsung-ha-washer-card`.

## Installazione

1. Copia il file `samsung-fridge-card.js` e incollalo nella cartella `config/www/` del tuo Home Assistant (se la cartella `www` non esiste, creala).
2. Se vuoi un'immagine personalizzata del frigo, salva un file PNG trasparente in `config/www/` e chiamalo `fridge.png`.
3. Vai in Home Assistant -> Impostazioni -> Plance -> Clicca i tre pallini in alto a destra -> Risorse.
4. Aggiungi una nuova risorsa con questi dati:
   - URL: `/local/samsung-fridge-card.js`
   - Tipo di risorsa: `Modulo JavaScript`
5. Riavvia Home Assistant o ricarica la pagina.

## Utilizzo nella Dashboard

Aggiungi una card Manuale alla tua plancia e usa questa configurazione. Sostituisci i nomi delle entità con quelli reali del tuo frigo:

```yaml
type: custom:samsung-fridge-card
name: Frigorifero Samsung
image: /local/fridge.png
entities:
  temp_fridge: number.frigo_fridge_target_temp
  temp_freezer: number.frigo_freezer_target_temp
  power_cool: switch.frigo_power_cool
  power_freeze: switch.frigo_power_freeze
  freezer_mode: select.frigo_freezer_mode_2
  door_fridge: binary_sensor.frigorifero_fridge_door
  door_freezer: binary_sensor.frigorifero_freezer_door
```
