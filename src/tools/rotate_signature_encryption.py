from __future__ import annotations

import asyncio

from src.db.session import SessionFactory
from src.services.signature_data_migration import rotate_signature_blobs


async def _run() -> None:
    async with SessionFactory() as session:
        report = await rotate_signature_blobs(session)
    print(
        "signature rotation complete: "
        f"signatories_rotated={report.signatories_reencrypted}, "
        f"invoices_rotated={report.invoices_reencrypted}, "
        f"signatories_failed={report.signatories_failed}, "
        f"invoices_failed={report.invoices_failed}"
    )
    if report.failed_signatory_ids:
        print(f"failed signatory ids: {report.failed_signatory_ids}")
    if report.failed_invoice_ids:
        print(f"failed invoice ids: {report.failed_invoice_ids}")


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
