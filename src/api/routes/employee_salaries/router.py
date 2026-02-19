from __future__ import annotations

from fastapi import APIRouter, File, Query, Request, Response, UploadFile, status

from src.api.deps import CurrentAdminDep, DBSessionDep, SettingsDep
from src.core.audit import audit_event, enforce_sensitive_export_step_up
from src.core.exceptions import AppException
from src.handlers.employee_salary import EmployeeSalaryHandler
from src.schemas.employee_salary import (
    EmployeeSalaryCreate,
    EmployeeSalaryImportResult,
    EmployeeSalaryRead,
    EmployeeSalaryUpdate,
)
from src.services.employee_salary_excel import EmployeeSalaryExcelService

router = APIRouter(prefix="/employee-salaries", tags=["employee-salaries"])
handler = EmployeeSalaryHandler()


@router.get("", response_model=list[EmployeeSalaryRead])
async def list_employee_salaries(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> list[EmployeeSalaryRead]:
    employees = await handler.list_employees(session, current_admin.transport_company_id)
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="employee_salary",
        action="list",
        metadata={"count": len(employees)},
    )
    return [EmployeeSalaryRead.model_validate(item) for item in employees]


@router.post("", response_model=EmployeeSalaryRead, status_code=status.HTTP_201_CREATED)
async def create_employee_salary(
    request: Request,
    payload: EmployeeSalaryCreate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> EmployeeSalaryRead:
    employee = await handler.create_employee(session, current_admin.transport_company_id, payload)
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="employee_salary",
        resource_id=str(employee.id),
        action="create",
    )
    return EmployeeSalaryRead.model_validate(employee)


@router.post("/import", response_model=EmployeeSalaryImportResult)
async def import_employee_salaries(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    file: UploadFile = File(...),
) -> EmployeeSalaryImportResult:
    content_type = (file.content_type or "").lower()
    allowed_content_types = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
    }
    if content_type and content_type not in allowed_content_types:
        raise AppException("Unsupported file format. Please upload an .xlsx file", status_code=400)

    file_bytes = await file.read()
    parsed = EmployeeSalaryExcelService.parse_salary_sheet(file_bytes)
    result = await handler.import_employees(
        session,
        current_admin.transport_company_id,
        parsed.rows,
        parsed.skipped,
    )
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="employee_salary",
        action="import",
        metadata={
            "created": result.created,
            "updated": result.updated,
            "skipped": len(result.skipped),
        },
    )
    return result


@router.get("/export")
async def export_employee_salaries(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    settings: SettingsDep,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=2100),
) -> Response:
    enforce_sensitive_export_step_up(request, settings)
    employees = await handler.list_employees(session, current_admin.transport_company_id)
    xlsx_bytes = EmployeeSalaryExcelService.generate_salary_sheet(
        employees=employees,
        month=month,
        year=year,
    )
    filename = f"salary_{year}_{month:02d}.xlsx"
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="employee_salary_sheet",
        action="export",
        metadata={"month": month, "year": year, "employee_count": len(employees)},
    )
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.patch("/{employee_id}", response_model=EmployeeSalaryRead)
async def update_employee_salary(
    request: Request,
    employee_id: int,
    payload: EmployeeSalaryUpdate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> EmployeeSalaryRead:
    employee = await handler.update_employee(
        session, current_admin.transport_company_id, employee_id, payload
    )
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="employee_salary",
        resource_id=str(employee.id),
        action="update",
    )
    return EmployeeSalaryRead.model_validate(employee)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee_salary(
    request: Request,
    employee_id: int,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> Response:
    await handler.delete_employee(session, current_admin.transport_company_id, employee_id)
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="employee_salary",
        resource_id=str(employee_id),
        action="delete",
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
