import csv
import sys
import os
from celery import shared_task
from django.db import transaction
from empresas.models import Contribuyente

# Increase CSV field size limit for very large fields
csv.field_size_limit(sys.maxsize)


@shared_task(bind=True)
def import_sunat_task(self, file_path):
    """
    Background task to import contribuyentes from a SUNAT .txt file.
    """
    total_count = 0
    batch_size = 5000
    batch = []

    try:
        with transaction.atomic():
            Contribuyente.objects.all().delete()

        with open(file_path, "r", encoding="latin-1") as f:
            reader = csv.reader(f, delimiter="|")
            # Skip header
            next(reader, None)

            for row in reader:
                if not row or len(row) < 11:
                    continue

                # Original mapping: Column 6 (idx 5), 7 (idx 6), 10 (idx 9)
                addr_parts = [row[5].strip(), row[6].strip(), row[9].strip()]
                full_address = " ".join([p for p in addr_parts if p and p != "-"])

                obj = Contribuyente(
                    ruc=row[0].strip(),
                    nombre_razon_social=row[1].strip(),
                    direccion=full_address,
                )
                batch.append(obj)

                if len(batch) >= batch_size:
                    with transaction.atomic():
                        Contribuyente.objects.bulk_create(batch)
                    total_count += len(batch)
                    batch = []
                    # Update progress info for the task
                    self.update_state(state="PROGRESS", meta={"current": total_count})

            if batch:
                with transaction.atomic():
                    Contribuyente.objects.bulk_create(batch)
                total_count += len(batch)

        # Clean up the file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        return {"status": "success", "imported": total_count}

    except Exception as e:
        # Clean up file even on failure
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e
