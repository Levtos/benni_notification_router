"""Unit tests for the pure routing engine."""
from __future__ import annotations

import pytest

from benni_notification_router.const import (
    ACT_PRIVATE_TIME, ACT_WORK_HOME,
    BIO_AWAKE, BIO_SLEEP, BIO_WAKING,
    EC_APPLIANCE_DONE, EC_DEVICE_HEALTH, EC_DOORBELL, EC_INFO, EC_SECURITY,
    MODE_CRITICAL, MODE_SILENT, MODE_SOFT,
    PRES_AWAY, PRES_HOME, PRES_PARENTS,
    ROUTE_BUS_ONLY, ROUTE_DASHBOARD, ROUTE_LIGHT, ROUTE_MEDIA,
    ROUTE_PERSISTENT, ROUTE_PUSH,
    SEV_CRITICAL, SEV_INFO, SEV_NORMAL, SEV_URGENT,
)
from benni_notification_router.routing import Context, Event, decide


def ctx(**kw) -> Context:
    return Context(**kw)


def test_doorbell_headset_prefers_light_push_over_audio():
    ev = Event(event_type=EC_DOORBELL, severity=SEV_NORMAL, title="Klingel", message="x")
    d = decide(ev, ctx(bio_state=BIO_AWAKE, headset_active=True, presence=PRES_HOME))
    assert ROUTE_PUSH in d.routes
    assert ROUTE_LIGHT in d.routes
    assert ROUTE_MEDIA not in d.routes
    assert "headset" in d.reason


def test_doorbell_sleep_is_soft_or_deferred():
    ev = Event(event_type=EC_DOORBELL, severity=SEV_NORMAL, title="t", message="m")
    d = decide(ev, ctx(bio_state=BIO_SLEEP, presence=PRES_HOME))
    # No loud audio at night
    assert ROUTE_MEDIA not in d.routes
    assert ROUTE_LIGHT not in d.routes
    # Defer to bus/dashboard
    assert ROUTE_BUS_ONLY in d.routes
    assert d.mode in (MODE_SOFT, MODE_SILENT)


def test_doorbell_sleep_critical_breaks_through():
    ev = Event(event_type=EC_DOORBELL, severity=SEV_CRITICAL, title="t", message="m")
    d = decide(ev, ctx(bio_state=BIO_SLEEP, presence=PRES_HOME))
    assert ROUTE_PUSH in d.routes
    assert d.mode == MODE_CRITICAL


def test_security_critical_always_push_and_persistent_even_under_dnd():
    ev = Event(event_type=EC_SECURITY, severity=SEV_CRITICAL, title="!", message="alarm")
    d = decide(ev, ctx(bio_state=BIO_SLEEP, dnd_override=True, presence=PRES_HOME))
    assert ROUTE_PUSH in d.routes
    assert ROUTE_PERSISTENT in d.routes


def test_security_normal_is_promoted_to_urgent():
    ev = Event(event_type=EC_SECURITY, severity=SEV_NORMAL, title="!", message="m")
    d = decide(ev, ctx(bio_state=BIO_AWAKE, presence=PRES_HOME))
    assert d.severity == SEV_URGENT
    assert ROUTE_PUSH in d.routes
    assert ROUTE_PERSISTENT in d.routes


def test_appliance_done_away_normal_push():
    ev = Event(event_type=EC_APPLIANCE_DONE, severity=SEV_NORMAL, title="Spülmaschine", message="fertig")
    d = decide(ev, ctx(presence=PRES_AWAY, bio_state=BIO_AWAKE))
    assert ROUTE_PUSH in d.routes
    assert ROUTE_MEDIA not in d.routes
    assert ROUTE_LIGHT not in d.routes


def test_appliance_done_sleep_is_deferred_or_soft():
    ev = Event(event_type=EC_APPLIANCE_DONE, severity=SEV_NORMAL, title="t", message="m")
    d = decide(ev, ctx(bio_state=BIO_SLEEP, presence=PRES_HOME))
    assert ROUTE_PUSH not in d.routes
    assert ROUTE_MEDIA not in d.routes
    assert d.mode in (MODE_SOFT, MODE_SILENT)


def test_private_time_masks_message():
    ev = Event(event_type=EC_INFO, severity=SEV_NORMAL, title="Termin", message="Arzttermin um 14:00")
    d = decide(ev, ctx(activity_state=ACT_PRIVATE_TIME, presence=PRES_HOME))
    assert d.masked is True
    assert "Arzttermin" not in d.message


def test_private_time_does_not_mask_critical():
    ev = Event(event_type=EC_SECURITY, severity=SEV_CRITICAL, title="!", message="break-in details")
    d = decide(ev, ctx(activity_state=ACT_PRIVATE_TIME, presence=PRES_HOME))
    assert d.masked is False
    assert d.message == "break-in details"


def test_quiet_mode_suppresses_audio():
    ev = Event(event_type=EC_DOORBELL, severity=SEV_NORMAL, title="t", message="m")
    d = decide(ev, ctx(quiet_mode_active=True, bio_state=BIO_AWAKE, presence=PRES_HOME))
    assert ROUTE_MEDIA not in d.routes


def test_bei_eltern_treated_as_home():
    ev = Event(event_type=EC_DOORBELL, severity=SEV_NORMAL, title="t", message="m")
    d_home = decide(ev, ctx(presence=PRES_HOME, bio_state=BIO_AWAKE))
    d_parents = decide(ev, ctx(presence=PRES_PARENTS, bio_state=BIO_AWAKE))
    assert set(d_home.routes) == set(d_parents.routes)


def test_work_home_less_intrusive():
    ev = Event(event_type=EC_INFO, severity=SEV_NORMAL, title="t", message="m")
    d = decide(ev, ctx(activity_state=ACT_WORK_HOME, presence=PRES_HOME, bio_state=BIO_AWAKE))
    assert ROUTE_MEDIA not in d.routes


def test_waking_softens_audio():
    ev = Event(event_type=EC_INFO, severity=SEV_NORMAL, title="t", message="m")
    d = decide(ev, ctx(bio_state=BIO_WAKING, presence=PRES_HOME))
    assert ROUTE_MEDIA not in d.routes


def test_device_health_no_audio():
    ev = Event(event_type=EC_DEVICE_HEALTH, severity=SEV_NORMAL, title="Batterie", message="20%")
    d = decide(ev, ctx(bio_state=BIO_AWAKE, presence=PRES_HOME))
    assert ROUTE_MEDIA not in d.routes


def test_dnd_blocks_low_severity_but_not_critical():
    ev_info = Event(event_type=EC_INFO, severity=SEV_INFO, title="t", message="m")
    d_info = decide(ev_info, ctx(dnd_override=True, presence=PRES_HOME, bio_state=BIO_AWAKE))
    assert ROUTE_PUSH not in d_info.routes
    assert ROUTE_MEDIA not in d_info.routes

    ev_crit = Event(event_type=EC_INFO, severity=SEV_CRITICAL, title="t", message="m")
    d_crit = decide(ev_crit, ctx(dnd_override=True, presence=PRES_HOME, bio_state=BIO_AWAKE))
    assert ROUTE_PUSH in d_crit.routes


def test_media_active_suppresses_audio():
    ev = Event(event_type=EC_INFO, severity=SEV_NORMAL, title="t", message="m")
    d = decide(ev, ctx(media_active=True, bio_state=BIO_AWAKE, presence=PRES_HOME))
    assert ROUTE_MEDIA not in d.routes


def test_decision_dict_is_serializable():
    ev = Event(event_type=EC_INFO, severity=SEV_NORMAL, title="t", message="m")
    d = decide(ev, ctx())
    raw = d.as_dict()
    assert raw["mode"] == d.mode
    assert "context" in raw
    assert isinstance(raw["routes"], list)
