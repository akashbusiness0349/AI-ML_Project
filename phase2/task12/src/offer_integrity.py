import hashlib
import json


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    )


def calculate_hash(data):
    content = canonical_json(data).encode("utf-8")

    return hashlib.sha256(content).hexdigest()


def create_signed_offer(offer):
    offer_copy = dict(offer)

    offer_hash = calculate_hash(offer_copy)

    offer_copy["integrity"] = {
        "algorithm": "SHA-256",
        "hash": offer_hash,
        "status": "SIGNED"
    }

    return offer_copy


def verify_offer(offer):
    if "integrity" not in offer:
        return False

    stored_hash = offer["integrity"]["hash"]

    content = dict(offer)
    del content["integrity"]

    calculated_hash = calculate_hash(content)

    return stored_hash == calculated_hash