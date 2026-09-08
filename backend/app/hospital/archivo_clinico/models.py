"""Modelos compartidos con Gestión de Pacientes; no duplicar tablas.
El aislamiento se obtiene mediante ClinicalRecord.patient_id -> Patient.tenant_id.
"""
from app.hospital.gestion_pacientes.models import ClinicalRecord, ClinicalRecordMovement

__all__ = ["ClinicalRecord", "ClinicalRecordMovement"]
