"""Identificación de HC, independiente de las referencias UUID del expediente."""
import re
import uuid


def numero_historia(document_type, document_number, is_nn=False):
    if document_type == "DNI" and not is_nn and re.fullmatch(r"[0-9]{8}", document_number or ""):
        return document_number
    return "HC-" + uuid.uuid4().hex


def numero_dni(patient):
    if patient.document_type == "DNI" and not patient.is_nn and re.fullmatch(r"[0-9]{8}", patient.dni or ""):
        return patient.dni
    return None
