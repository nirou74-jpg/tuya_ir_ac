# Tuya IR AC — Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/VOTRE_PSEUDO/tuya_ir_ac.svg)](https://github.com/VOTRE_PSEUDO/tuya_ir_ac/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Intégration personnalisée pour contrôler une **climatisation infrarouge Tuya** (catégorie `infrared_ac`, pilotée par un blaster/thermostat IR SmartLife) qui apparaît comme *unsupported* dans l'intégration Tuya officielle de Home Assistant.

Elle expose une entité `climate` native (carte thermostat) en s'appuyant sur l'**API Cloud Tuya OpenAPI** : lecture de l'état (polling) et envoi des commandes via votre `client_id` / `secret_key` / `device_id`.

## Fonctionnalités

- Entité `climate` complète, configurable **entièrement via l'interface** (aucun YAML).
- Marche / arrêt, mode, vitesse de ventilation, température cible.
- Rafraîchissement automatique de l'état toutes les 30 s + actualisation immédiate après chaque commande.
- Multi-régions (EU, US, CN, IN).

| Capacité HA | Code Tuya | Valeurs |
|---|---|---|
| Marche/arrêt | `switch` | `true` / `false` |
| Mode | `M` | 0 Cool · 1 Heat · 2 Auto · 3 Dry · 4 Fan only |
| Ventilation | `F` | 0 auto · 1 low · 2 medium · 3 high |
| Température | `T` | 16 – 30 °C (pas de 1 °C) |

L'état est lu depuis `/v1.0/devices/{device_id}/status` (`power`, `mode`, `temp`, `wind`).

## Prérequis

1. Un compte sur la [Tuya IoT Platform](https://iot.tuya.com/) avec un projet Cloud.
2. L'appareil (la clim IR) lié à ce projet.
3. Les identifiants du projet : **Access ID** (`client_id`) et **Access Secret** (`secret_key`).
4. Le **Device ID** de la clim (visible dans la liste des appareils du projet Cloud, ou via l'app SmartLife → appareil → infos).

> ⚠️ Vérifiez la **région (Data Center)** de votre projet Tuya (Europe, US, etc.). Une mauvaise région provoque une erreur d'authentification.

## Installation via HACS

### En dépôt personnalisé (custom repository)

1. Ouvrez **HACS** dans Home Assistant.
2. Menu (3 points en haut à droite) → **Dépôts personnalisés**.
3. URL : `https://github.com/VOTRE_PSEUDO/tuya_ir_ac` — Type : **Integration**.
4. Cliquez **Ajouter**, puis recherchez **Tuya IR AC** et téléchargez-le.
5. **Redémarrez Home Assistant**.

### Installation manuelle (sans HACS)

Copiez le dossier `custom_components/tuya_ir_ac` dans le répertoire `config/custom_components/` de votre instance, puis redémarrez Home Assistant.

## Configuration

1. **Paramètres → Appareils et services → Ajouter une intégration**.
2. Cherchez **Tuya IR AC**.
3. Renseignez :
   - **Client ID** (Access ID)
   - **Secret Key** (Access Secret)
   - **Device ID** de la clim
   - **Région** du datacenter Tuya (EU par défaut)
4. Les identifiants sont validés immédiatement (récupération du token + lecture de l'état). Une entité `climate.climatisation_ir` est créée.

## Dépannage

- **« Client ID ou Secret Key invalide »** → vérifiez les identifiants et surtout la **région** du projet.
- **« Impossible de joindre l'API Tuya ou device introuvable »** → vérifiez le `device_id` et que l'appareil est bien rattaché au projet Cloud.
- **Le mode affiché ne correspond pas** → ouvrez une *issue* avec un retour de `/status` clim allumée.
- **Network sandbox (Docker)** : l'intégration appelle `openapi.tuya*.com`. Assurez-vous que le conteneur HA a un accès sortant HTTPS.

## Avertissement

Projet non affilié à Tuya ni à Anthropic. Fourni « tel quel », sans garantie. Utilisez vos identifiants Tuya sous votre responsabilité.

## Licence

[MIT](LICENSE)
