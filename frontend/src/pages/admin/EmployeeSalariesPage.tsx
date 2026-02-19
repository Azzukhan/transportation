import { useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createEmployeeSalary,
  deleteEmployeeSalary,
  exportEmployeeSalaries,
  importEmployeeSalaries,
  listEmployeeSalaries,
  updateEmployeeSalary,
} from "@/api/employeeSalaries";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { Download, Pencil, Trash2, Upload, UserRoundCog, UserRoundPlus } from "lucide-react";
import { toast } from "sonner";
import type { EmployeeSalaryApi } from "@/types";

type FormState = {
  employeeName: string;
  workPermitNo: string;
  personalNo: string;
  bankNameRoutingNo: string;
  bankAccountNo: string;
  daysAbsent: string;
  fixedPortion: string;
  variablePortion: string;
  totalPayment: string;
  onLeave: boolean;
};

const blankForm: FormState = {
  employeeName: "",
  workPermitNo: "",
  personalNo: "",
  bankNameRoutingNo: "",
  bankAccountNo: "",
  daysAbsent: "",
  fixedPortion: "",
  variablePortion: "",
  totalPayment: "",
  onLeave: false,
};

const monthOptions = [
  { value: 1, label: "January" },
  { value: 2, label: "February" },
  { value: 3, label: "March" },
  { value: 4, label: "April" },
  { value: 5, label: "May" },
  { value: 6, label: "June" },
  { value: 7, label: "July" },
  { value: 8, label: "August" },
  { value: 9, label: "September" },
  { value: 10, label: "October" },
  { value: 11, label: "November" },
  { value: 12, label: "December" },
];

const toForm = (item: EmployeeSalaryApi): FormState => ({
  employeeName: item.employee_name,
  workPermitNo: item.work_permit_no,
  personalNo: item.personal_no,
  bankNameRoutingNo: item.bank_name_routing_no ?? "",
  bankAccountNo: item.bank_account_no,
  daysAbsent: item.days_absent == null ? "" : String(item.days_absent),
  fixedPortion: item.fixed_portion,
  variablePortion: item.variable_portion,
  totalPayment: item.total_payment,
  onLeave: item.on_leave,
});

const EmployeeSalariesPage = () => {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<FormState>(blankForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [exportMonth, setExportMonth] = useState<number>(new Date().getMonth() + 1);
  const [exportYear, setExportYear] = useState<number>(new Date().getFullYear());
  const importInputRef = useRef<HTMLInputElement | null>(null);

  const salariesQuery = useQuery({
    queryKey: ["employee-salaries"],
    queryFn: listEmployeeSalaries,
  });

  const createMutation = useMutation({
    mutationFn: createEmployeeSalary,
    onSuccess: () => {
      toast.success("Employee added.");
      setForm(blankForm);
      queryClient.invalidateQueries({ queryKey: ["employee-salaries"] });
    },
    onError: () => toast.error("Failed to add employee."),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: FormState }) =>
      updateEmployeeSalary(id, {
        employeeName: payload.employeeName,
        workPermitNo: payload.workPermitNo,
        personalNo: payload.personalNo,
        bankNameRoutingNo: payload.bankNameRoutingNo,
        bankAccountNo: payload.bankAccountNo,
        daysAbsent: payload.daysAbsent === "" ? null : Number(payload.daysAbsent),
        fixedPortion: payload.fixedPortion,
        variablePortion: payload.variablePortion,
        totalPayment: payload.totalPayment || undefined,
        onLeave: payload.onLeave,
      }),
    onSuccess: () => {
      toast.success("Employee updated.");
      setForm(blankForm);
      setEditingId(null);
      queryClient.invalidateQueries({ queryKey: ["employee-salaries"] });
    },
    onError: () => toast.error("Failed to update employee."),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEmployeeSalary,
    onSuccess: () => {
      toast.success("Employee deleted.");
      queryClient.invalidateQueries({ queryKey: ["employee-salaries"] });
    },
    onError: () => toast.error("Failed to delete employee."),
  });

  const importMutation = useMutation({
    mutationFn: importEmployeeSalaries,
    onSuccess: (result) => {
      const skippedCount = result.skipped.length;
      const summary = `Imported salaries. Created: ${result.created}, Updated: ${result.updated}, Skipped: ${skippedCount}.`;
      if (skippedCount > 0) {
        const details = result.skipped
          .slice(0, 3)
          .map((item) => `Row ${item.row_number}: ${item.reason}`)
          .join(" | ");
        toast.warning(`${summary} ${details}`);
      } else {
        toast.success(summary);
      }
      queryClient.invalidateQueries({ queryKey: ["employee-salaries"] });
    },
    onError: () => toast.error("Failed to import salary Excel."),
  });

  const sortedRows = useMemo(
    () => [...(salariesQuery.data ?? [])].sort((a, b) => a.id - b.id),
    [salariesQuery.data],
  );

  const ensureValid = (): boolean => {
    if (!form.employeeName.trim()) return false;
    if (!/^\d{8}$/.test(form.workPermitNo.trim())) return false;
    if (!/^\d{14}$/.test(form.personalNo.trim())) return false;
    if (!form.bankAccountNo.trim()) return false;
    return true;
  };

  const onSubmit = () => {
    if (!ensureValid()) {
      toast.error("Please fill required fields. Work Permit must be 8 digits, Personal No must be 14 digits.");
      return;
    }
    const payload = {
      employeeName: form.employeeName.trim(),
      workPermitNo: form.workPermitNo.trim(),
      personalNo: form.personalNo.trim(),
      bankNameRoutingNo: form.bankNameRoutingNo.trim() || undefined,
      bankAccountNo: form.bankAccountNo.trim(),
      daysAbsent: form.daysAbsent === "" ? null : Number(form.daysAbsent),
      fixedPortion: form.fixedPortion || "0",
      variablePortion: form.variablePortion || "0",
      totalPayment: form.totalPayment || undefined,
      onLeave: form.onLeave,
    };
    if (editingId == null) {
      createMutation.mutate(payload);
    } else {
      updateMutation.mutate({ id: editingId, payload: form });
    }
  };

  const onImportFileSelected = (file: File | null) => {
    if (!file) return;
    importMutation.mutate(file);
  };

  return (
    <div className="space-y-5 max-w-7xl">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center">
                <UserRoundCog size={22} />
              </div>
              <div>
                <h1 className="font-display text-3xl font-bold">Employee Salaries</h1>
                <p className="text-muted-foreground text-sm">Manage salary data and download monthly payroll Excel.</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <input
                ref={importInputRef}
                type="file"
                accept=".xlsx"
                className="hidden"
                onChange={(e) => {
                  onImportFileSelected(e.target.files?.[0] ?? null);
                  e.currentTarget.value = "";
                }}
              />
              <Button
                variant="outline"
                onClick={() => importInputRef.current?.click()}
                disabled={importMutation.isPending}
              >
                <Upload size={14} className="mr-1.5" /> Import .xlsx
              </Button>
              <select
                value={exportMonth}
                onChange={(e) => setExportMonth(Number(e.target.value))}
                className="h-10 rounded-lg border border-border bg-background px-3 text-sm"
              >
                {monthOptions.map((month) => (
                  <option key={month.value} value={month.value}>
                    {month.label}
                  </option>
                ))}
              </select>
              <Input
                type="number"
                value={exportYear}
                min={2000}
                max={2100}
                onChange={(e) => setExportYear(Number(e.target.value))}
                className="w-28"
              />
              <Button
                variant="outline"
                onClick={async () => {
                  try {
                    const blob = await exportEmployeeSalaries(exportMonth, exportYear);
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `salary_${exportYear}_${String(exportMonth).padStart(2, "0")}.xlsx`;
                    a.click();
                    URL.revokeObjectURL(url);
                  } catch {
                    toast.error("Failed to export salary sheet.");
                  }
                }}
              >
                <Download size={14} className="mr-1.5" /> Export .xlsx
              </Button>
            </div>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.05}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60 space-y-4">
          <h2 className="font-semibold text-lg flex items-center gap-2">
            <UserRoundPlus size={17} />
            {editingId == null ? "Add New Employee" : `Edit Employee #${editingId}`}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <Input placeholder="Employee name *" value={form.employeeName} onChange={(e) => setForm({ ...form, employeeName: e.target.value })} />
            <Input placeholder="Work Permit No (8 digits) *" value={form.workPermitNo} onChange={(e) => setForm({ ...form, workPermitNo: e.target.value })} />
            <Input placeholder="Personal No (14 digits) *" value={form.personalNo} onChange={(e) => setForm({ ...form, personalNo: e.target.value })} />
            <Input placeholder="Bank Name & Routing No" value={form.bankNameRoutingNo} onChange={(e) => setForm({ ...form, bankNameRoutingNo: e.target.value })} />
            <Input placeholder="Bank Account No *" value={form.bankAccountNo} onChange={(e) => setForm({ ...form, bankAccountNo: e.target.value })} />
            <Input placeholder="No of Days Absent" type="number" min={0} max={31} value={form.daysAbsent} onChange={(e) => setForm({ ...form, daysAbsent: e.target.value })} />
            <Input placeholder="Fixed Portion" type="number" step="0.01" value={form.fixedPortion} onChange={(e) => setForm({ ...form, fixedPortion: e.target.value })} />
            <Input placeholder="Variable Portion" type="number" step="0.01" value={form.variablePortion} onChange={(e) => setForm({ ...form, variablePortion: e.target.value })} />
            <Input placeholder="Total Payment (optional)" type="number" step="0.01" value={form.totalPayment} onChange={(e) => setForm({ ...form, totalPayment: e.target.value })} />
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <label className="text-sm font-medium flex items-center gap-2">
              On Leave
              <Switch checked={form.onLeave} onCheckedChange={(checked) => setForm({ ...form, onLeave: checked })} />
            </label>
            <div className="flex gap-2">
              <Button onClick={onSubmit} disabled={createMutation.isPending || updateMutation.isPending}>
                {editingId == null ? "Add Employee" : "Update Employee"}
              </Button>
              {editingId != null && (
                <Button
                  variant="outline"
                  onClick={() => {
                    setEditingId(null);
                    setForm(blankForm);
                  }}
                >
                  Cancel
                </Button>
              )}
            </div>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.1}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          {salariesQuery.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-border/60">
              <table className="w-full text-sm min-w-[1200px]">
                <thead className="bg-muted/45">
                  <tr className="text-left">
                    <th className="px-3 py-3">#</th>
                    <th className="px-3 py-3">Employee Name</th>
                    <th className="px-3 py-3">Work Permit</th>
                    <th className="px-3 py-3">Personal No</th>
                    <th className="px-3 py-3">Bank Name & Routing</th>
                    <th className="px-3 py-3">Bank Account</th>
                    <th className="px-3 py-3">Absent Days</th>
                    <th className="px-3 py-3">Fixed</th>
                    <th className="px-3 py-3">Variable</th>
                    <th className="px-3 py-3">Total</th>
                    <th className="px-3 py-3">On Leave</th>
                    <th className="px-3 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedRows.map((row) => (
                    <tr key={row.id} className="border-t border-border/60">
                      <td className="px-3 py-2">#{row.id}</td>
                      <td className="px-3 py-2">{row.employee_name}</td>
                      <td className="px-3 py-2">{row.work_permit_no}</td>
                      <td className="px-3 py-2">{row.personal_no}</td>
                      <td className="px-3 py-2">{row.bank_name_routing_no || "-"}</td>
                      <td className="px-3 py-2">{row.bank_account_no}</td>
                      <td className="px-3 py-2">{row.days_absent ?? "-"}</td>
                      <td className="px-3 py-2">{row.fixed_portion}</td>
                      <td className="px-3 py-2">{row.variable_portion}</td>
                      <td className="px-3 py-2 font-semibold">{row.total_payment}</td>
                      <td className="px-3 py-2">{row.on_leave ? "Yes" : "No"}</td>
                      <td className="px-3 py-2">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingId(row.id);
                              setForm(toForm(row));
                            }}
                          >
                            <Pencil size={14} />
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => {
                              deleteMutation.mutate(row.id);
                            }}
                          >
                            <Trash2 size={14} />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {sortedRows.length === 0 && (
                    <tr>
                      <td colSpan={12} className="px-3 py-8 text-center text-muted-foreground">
                        No employee salary records yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </AnimatedSection>
    </div>
  );
};

export default EmployeeSalariesPage;
