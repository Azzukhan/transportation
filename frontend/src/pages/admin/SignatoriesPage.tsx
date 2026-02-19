import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createSignatory,
  downloadSignatorySignature,
  deleteSignatory,
  listSignatories,
  updateSignatory,
} from "@/api/invoices";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Pencil, Plus, Save, Signature, Trash2, X } from "lucide-react";

const SignatoriesPage = () => {
  const qc = useQueryClient();
  const [newName, setNewName] = useState("");
  const [newFile, setNewFile] = useState<File | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editFile, setEditFile] = useState<File | null>(null);
  const [previewUrls, setPreviewUrls] = useState<Record<number, string>>({});

  const signatories = useQuery({
    queryKey: ["signatories"],
    queryFn: listSignatories,
  });

  const sortedSignatories = useMemo(
    () => [...(signatories.data ?? [])].sort((a, b) => a.id - b.id),
    [signatories.data],
  );

  useEffect(() => {
    return () => {
      Object.values(previewUrls).forEach((url) => URL.revokeObjectURL(url));
    };
  }, [previewUrls]);

  const createMutation = useMutation({
    mutationFn: createSignatory,
    onSuccess: () => {
      toast.success("Signatory added.");
      setNewName("");
      setNewFile(null);
      qc.invalidateQueries({ queryKey: ["signatories"] });
    },
    onError: (error: unknown) => {
      toast.error(error instanceof Error ? error.message : "Failed to add signatory.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, name, file }: { id: number; name: string; file?: File }) =>
      updateSignatory(id, { name, file }),
    onSuccess: () => {
      toast.success("Signatory updated.");
      setEditingId(null);
      qc.invalidateQueries({ queryKey: ["signatories"] });
    },
    onError: (error: unknown) => {
      toast.error(error instanceof Error ? error.message : "Failed to update signatory.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteSignatory,
    onSuccess: () => {
      toast.success("Signatory deleted.");
      qc.invalidateQueries({ queryKey: ["signatories"] });
    },
    onError: (error: unknown) => {
      toast.error(error instanceof Error ? error.message : "Failed to delete signatory.");
    },
  });

  const handleCreate = async () => {
    const name = newName.trim();
    if (!name || !newFile) {
      toast.error("Name and signature image are required.");
      return;
    }
    createMutation.mutate({ name, file: newFile });
  };

  const startEdit = (id: number, name: string) => {
    setEditingId(id);
    setEditName(name);
    setEditFile(null);
  };

  const handleUpdate = async () => {
    if (!editingId) return;
    const name = editName.trim();
    if (!name) {
      toast.error("Name is required.");
      return;
    }
    updateMutation.mutate({ id: editingId, name, file: editFile ?? undefined });
  };

  const loadPreview = async (id: number) => {
    if (previewUrls[id]) return;
    try {
      const { blob } = await downloadSignatorySignature(id);
      const nextUrl = URL.createObjectURL(blob);
      setPreviewUrls((prev) => ({ ...prev, [id]: nextUrl }));
    } catch {
      toast.error("Unable to load signature preview.");
    }
  };

  return (
    <div className="space-y-5 max-w-6xl">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center bg-accent/15 text-accent">
              <Signature size={22} />
            </div>
            <div>
              <h1 className="font-display text-3xl font-bold">Signatories</h1>
              <p className="text-muted-foreground text-sm">Manage prepared-by names and signature images.</p>
            </div>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.08}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60 space-y-4">
          <h2 className="font-semibold text-lg">Add Signatory</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Name (e.g. Roshan)"
            />
            <Input
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/svg+xml,image/webp"
              onChange={(e) => setNewFile(e.target.files?.[0] ?? null)}
            />
          </div>
          <Button
            onClick={handleCreate}
            disabled={createMutation.isPending}
            className="bg-accent-gradient text-accent-foreground border-0"
          >
            <Plus size={15} className="mr-1.5" /> {createMutation.isPending ? "Adding..." : "Add Signatory"}
          </Button>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.12}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="overflow-x-auto rounded-xl border border-border/60">
            <table className="w-full text-sm">
              <thead className="bg-muted/45">
                <tr className="text-left">
                  <th className="px-4 py-3 font-semibold text-muted-foreground">ID</th>
                  <th className="px-4 py-3 font-semibold text-muted-foreground">Name</th>
                  <th className="px-4 py-3 font-semibold text-muted-foreground">Signature</th>
                  <th className="px-4 py-3 font-semibold text-muted-foreground">Preview</th>
                  <th className="px-4 py-3 font-semibold text-muted-foreground text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {signatories.isLoading ? (
                  <tr>
                    <td className="px-4 py-5 text-muted-foreground" colSpan={5}>Loading signatories...</td>
                  </tr>
                ) : sortedSignatories.length === 0 ? (
                  <tr>
                    <td className="px-4 py-5 text-muted-foreground" colSpan={5}>No signatories found.</td>
                  </tr>
                ) : (
                  sortedSignatories.map((item) => {
                    const editing = editingId === item.id;
                    return (
                      <tr key={item.id} className="border-t border-border/60">
                        <td className="px-4 py-3">#{item.id}</td>
                        <td className="px-4 py-3">
                          {editing ? (
                            <Input value={editName} onChange={(e) => setEditName(e.target.value)} />
                          ) : (
                            item.name
                          )}
                        </td>
                        <td className="px-4 py-3">
                          {editing ? (
                            <div className="space-y-2">
                              <Input
                                type="file"
                                accept="image/png,image/jpeg,image/jpg,image/svg+xml,image/webp"
                                onChange={(e) => setEditFile(e.target.files?.[0] ?? null)}
                              />
                              <p className="text-xs text-muted-foreground">
                                Leave empty to keep current signature image.
                              </p>
                            </div>
                          ) : (
                            <span className="text-xs text-muted-foreground">
                              Stored in DB{item.signature_image_mime ? ` (${item.signature_image_mime})` : ""}
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          {previewUrls[item.id] ? (
                            <img
                              src={previewUrls[item.id]}
                              alt={`${item.name} signature`}
                              className="h-10 w-28 rounded border border-border/60 bg-white object-contain"
                            />
                          ) : item.has_signature ? (
                            <Button size="sm" variant="outline" onClick={() => void loadPreview(item.id)}>
                              Load Preview
                            </Button>
                          ) : (
                            <span className="text-xs text-muted-foreground">No image</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-end gap-2">
                            {editing ? (
                              <>
                                <Button size="sm" onClick={handleUpdate} disabled={updateMutation.isPending}>
                                  <Save size={14} className="mr-1" /> Save
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setEditingId(null)}
                                >
                                  <X size={14} className="mr-1" /> Cancel
                                </Button>
                              </>
                            ) : (
                              <>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => startEdit(item.id, item.name)}
                                >
                                  <Pencil size={14} className="mr-1" /> Edit
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => deleteMutation.mutate(item.id)}
                                  disabled={deleteMutation.isPending}
                                >
                                  <Trash2 size={14} className="mr-1" /> Delete
                                </Button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </AnimatedSection>
    </div>
  );
};

export default SignatoriesPage;
