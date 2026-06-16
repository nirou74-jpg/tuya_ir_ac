"""Climate platform for Tuya IR AC."""
from __future__ import annotations

import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TuyaAcCoordinator
from .const import (
    DOMAIN,
    F_TO_FAN,
    FAN_TO_F,
    M_TO_MODE,
    MODE_TO_M,
    TEMP_MAX,
    TEMP_MIN,
    TEMP_STEP,
)

_LOGGER = logging.getLogger(__name__)

# HA HVACMode <-> mode interne (cool/heat/auto/dry/fan_only)
HA_HVAC_TO_INTERNAL = {
    HVACMode.COOL: "cool",
    HVACMode.HEAT: "heat",
    HVACMode.AUTO: "auto",
    HVACMode.DRY: "dry",
    HVACMode.FAN_ONLY: "fan_only",
}
INTERNAL_TO_HA_HVAC = {v: k for k, v in HA_HVAC_TO_INTERNAL.items()}

FAN_MODES = ["auto", "low", "medium", "high"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TuyaAcCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TuyaIrAcClimate(coordinator, entry)])


class TuyaIrAcClimate(CoordinatorEntity, ClimateEntity):
    """Représente la climatisation IR Tuya."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = TEMP_STEP
    _attr_min_temp = TEMP_MIN
    _attr_max_temp = TEMP_MAX
    _attr_fan_modes = FAN_MODES
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.COOL,
        HVACMode.HEAT,
        HVACMode.AUTO,
        HVACMode.DRY,
        HVACMode.FAN_ONLY,
    ]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: TuyaAcCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{coordinator.device_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            name="Climatisation IR",
            manufacturer="Tuya",
            model="Infrared AC",
        )

    # ------------------------------------------------------------------ #
    # Helpers de lecture du status
    # ------------------------------------------------------------------ #
    @property
    def _status(self) -> dict:
        return self.coordinator.data or {}

    def _get_int(self, key: str, default: int = 0) -> int:
        val = self._status.get(key, default)
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    @property
    def _is_on(self) -> bool:
        # status renvoie "power": "0"/"1"
        return self._get_int("power", 0) == 1

    # ------------------------------------------------------------------ #
    # État exposé à HA
    # ------------------------------------------------------------------ #
    @property
    def hvac_mode(self) -> HVACMode:
        # Éteint -> OFF pour que le bouton marche/arrêt de la carte soit correct.
        # La consigne (target_temperature) et la ventilation (fan_mode) restent
        # lisibles même éteint car elles lisent directement le status.
        if not self._is_on:
            return HVACMode.OFF
        internal = M_TO_MODE.get(self._get_int("mode", 0), "cool")
        return INTERNAL_TO_HA_HVAC.get(internal, HVACMode.COOL)

    @property
    def icon(self) -> str:
        # Icône dynamique selon la vitesse de ventilation
        # (mêmes icônes que le sélecteur de ventilation).
        if not self._is_on:
            return "mdi:fan-off"
        fan = F_TO_FAN.get(self._get_int("wind", 0), "auto")
        return {
            "auto": "mdi:fan-auto",
            "low": "mdi:fan-speed-1",
            "medium": "mdi:fan-speed-2",
            "high": "mdi:fan-speed-3",
        }.get(fan, "mdi:fan")

    @property
    def extra_state_attributes(self) -> dict:
        # Mode et ventilation mémorisés, visibles même clim éteinte.
        internal = M_TO_MODE.get(self._get_int("mode", 0), "cool")
        return {
            "mode_reel": internal,
            "ventilation_reelle": F_TO_FAN.get(self._get_int("wind", 0), "auto"),
            "consigne": self._get_int("temp", 25),
        }

    @property
    def fan_mode(self) -> str:
        return F_TO_FAN.get(self._get_int("wind", 0), "auto")

    @property
    def target_temperature(self) -> float | None:
        return float(self._get_int("temp", 25))

    # ------------------------------------------------------------------ #
    # Commandes
    # ------------------------------------------------------------------ #
    async def async_set_temperature(self, **kwargs) -> None:
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        temp = int(max(TEMP_MIN, min(TEMP_MAX, round(temp))))
        await self.coordinator.async_send([{"code": "T", "value": temp}])

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        f_val = FAN_TO_F.get(fan_mode)
        if f_val is None:
            return
        await self.coordinator.async_send([{"code": "F", "value": f_val}])

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_send([{"code": "switch", "value": False}])
            return

        internal = HA_HVAC_TO_INTERNAL.get(hvac_mode)
        m_val = MODE_TO_M.get(internal)
        if m_val is None:
            return
        # Envoyer le mode allume déjà la clim (power passe à 1) ;
        # l'API n'accepte qu'une commande à la fois, donc pas de switch ici.
        await self.coordinator.async_send([{"code": "M", "value": m_val}])

    async def async_turn_on(self) -> None:
        await self.coordinator.async_send([{"code": "switch", "value": True}])

    async def async_turn_off(self) -> None:
        await self.coordinator.async_send([{"code": "switch", "value": False}])

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
