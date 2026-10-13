"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { UploadDropzone } from "@/components/UploadDropzone";
import { 
  Plus, 
  Library, 
  Sparkles, 
  ImageIcon, 
  Mic, 
  FileText, 
  Trash2, 
  ChevronRight, 
  Zap, 
  X,
  Calendar
} from "lucide-react";

export default function WorkspaceLibraryPage() {
  const [libraryItems, setLibraryItems] = useState<any[]>([]);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState("");
  const [assetType, setAssetType] = useState<"photo" | "audio" | "document">("photo");
  const [triggerPrompt, setTriggerPrompt] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [libraryFilter, setLibraryFilter] = useState<"all" | "photo" | "audio" | "document">("all");

  useEffect(() => {
    loadLibraryItems();
  }, []);

  const loadLibraryItems = async () => {
    try {
      const res = await fetch("/api/library/items");
      if (res.ok) {
        const data = await res.json();
        setLibraryItems(data.items || []);
      }
    } catch (e) {}
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("name", uploadName);
      formData.append("asset_type", assetType);
      formData.append("trigger_prompt", triggerPrompt);

      const res = await fetch("/api/library/upload", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        await loadLibraryItems();
        setIsUploadOpen(false);
        setUploadFile(null);
        setUploadName("");
        setTriggerPrompt("");
      }
    } catch (e) {
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteLibraryItem = async (id: string) => {
    try {
      const res = await fetch(`/api/library/items/${id}`, { method: "DELETE" });
      if (res.ok) {
        loadLibraryItems();
      }
    } catch (e) {}
  };

  const filteredLibrary = libraryItems.filter(item => {
    if (libraryFilter === "all") return true;
    return item.asset_type === libraryFilter;
  });

  return (
    <AppShell fullWidth={true}>
      <div className="space-y-6">
        <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 flex items-center justify-between shadow-2xs">
          <div>
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white">Biblioteca de Recursos Multimedia</h2>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
              Suba fotos, notas de voz y documentos PDF. Configure las condiciones de activación para su envío por WhatsApp.
            </p>
          </div>

          <Button
            onClick={() => setIsUploadOpen(true)}
            className="bg-neutral-900 hover:bg-neutral-800 text-white dark:bg-white dark:hover:bg-neutral-200 dark:text-neutral-950 font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-2 shadow-xs cursor-pointer"
          >
            <Plus className="size-4" />
            Añadir Recurso
          </Button>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2">
          {(["all", "photo", "audio", "document"] as const).map(f => (
            <button
              key={f}
              onClick={() => setLibraryFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                libraryFilter === f
                  ? "bg-[#b9fa01] text-black font-semibold shadow-xs"
                  : "bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
              }`}
            >
              {f === "all" ? `Todos (${libraryItems.length})` : f === "photo" ? "Fotos" : f === "audio" ? "Audios" : "Documentos"}
            </button>
          ))}
        </div>

          {/* Grid of Assets */}
          {filteredLibrary.length === 0 ? (
            <div className="bg-white dark:bg-[#252525] border border-dashed border-neutral-300 dark:border-[#444] rounded-xl p-12 text-center flex flex-col items-center justify-center space-y-3 shadow-xs">
              <Library className="size-10 text-emerald-600 dark:text-amber-400" />
              <h3 className="text-base font-semibold text-neutral-900 dark:text-white">Tu Biblioteca está vacía</h3>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 max-w-sm">
                Sube la lista de precios, audios de bienvenida de la doctora o mapas de la clínica.
              </p>
              <Button onClick={() => setIsUploadOpen(true)} className="bg-emerald-600 hover:bg-emerald-700 dark:bg-amber-500 dark:hover:bg-amber-600 text-white dark:text-neutral-950 font-semibold text-xs px-4 py-2 rounded-xl shadow-xs">
                Añadir el Primer Recurso
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {filteredLibrary.map(item => (
                <div key={item.id} className="bg-white dark:bg-[#252525] border border-neutral-200/80 dark:border-[#333] rounded-xl p-4 space-y-3 flex flex-col justify-between group hover:border-emerald-500/50 dark:hover:border-amber-500/50 transition-all shadow-xs">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="p-2 rounded-lg bg-emerald-50 dark:bg-amber-500/10 text-emerald-700 dark:text-amber-400">
                          {item.asset_type === "photo" ? <ImageIcon className="size-4" /> : item.asset_type === "audio" ? <Mic className="size-4" /> : <FileText className="size-4" />}
                        </div>
                        <span className="text-xs font-semibold text-neutral-900 dark:text-white truncate max-w-[160px]">{item.name}</span>
                      </div>
                      <button onClick={() => handleDeleteLibraryItem(item.id)} className="text-neutral-400 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Trash2 className="size-4" />
                      </button>
                    </div>

                    <div className="bg-neutral-50 dark:bg-[#1a1a1a] border border-neutral-200 dark:border-[#333] p-3 rounded-lg space-y-1">
                      <span className="text-[10px] font-bold text-emerald-600 dark:text-amber-400 uppercase tracking-wider flex items-center gap-1">
                        <Zap className="size-3" /> Detonante:
                      </span>
                      <p className="text-xs text-neutral-600 dark:text-neutral-300 italic">"{item.trigger_prompt}"</p>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-neutral-100 dark:border-[#333] flex items-center justify-between text-[11px]">
                    <a href={item.url} target="_blank" rel="noreferrer" className="text-emerald-600 dark:text-amber-400 hover:underline font-medium flex items-center gap-1">
                      Ver archivo <ChevronRight className="size-3" />
                    </a>
                    <span className="text-neutral-400">{Math.round((item.size_bytes || 0) / 1024)} KB</span>
                  </div>
                </div>
              ))}
            </div>
          )}

        </div>

      {/* MODAL: SUBIR RECURSO A LA BIBLIOTECA */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
          <div className="bg-white dark:bg-[#141418] border border-neutral-200 dark:border-[#27272a] rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-neutral-100 dark:border-[#22222a] pb-3">
              <div className="flex items-center gap-2">
                <Library className="size-5 text-emerald-600 dark:text-[#b9fa01]" />
                <h3 className="text-base font-bold text-neutral-900 dark:text-white">Añadir Recurso a la Memoria de Firby</h3>
              </div>
              <button onClick={() => setIsUploadOpen(false)} className="text-neutral-400 hover:text-neutral-700 dark:hover:text-white p-1 cursor-pointer">
                <X className="size-4" />
              </button>
            </div>

            {/* BENCHO UPLOAD DROPZONE */}
            <div className="flex flex-col items-center justify-center py-2 bg-neutral-50 dark:bg-[#18181d] border border-neutral-200/80 dark:border-[#27272a] rounded-2xl">
              <UploadDropzone
                speed={60}
                bounce={45}
                corner={18}
                onUploadComplete={(file, rawFile) => {
                  setUploadName(file.name);
                  if (rawFile) setUploadFile(rawFile);
                  if (["PNG", "JPG", "JPEG", "WEBP", "GIF", "SVG"].includes(file.ext)) setAssetType("photo");
                  else if (["MP3", "WAV", "OGG", "M4A"].includes(file.ext)) setAssetType("audio");
                  else setAssetType("document");
                }}
              />
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">

              <div className="space-y-1">
                <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">Nombre del Recurso</label>
                <input
                  type="text"
                  required
                  value={uploadName}
                  onChange={(e) => setUploadName(e.target.value)}
                  placeholder="Ej: Catalogo Tratamientos 2026.pdf"
                  className="w-full px-3 py-2 rounded-lg bg-neutral-50 dark:bg-[#18181d] border border-neutral-200 dark:border-[#27272a] text-xs text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-lime-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">Tipo de Recurso</label>
                <select
                  value={assetType}
                  onChange={(e: any) => setAssetType(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-neutral-50 dark:bg-[#18181d] border border-neutral-200 dark:border-[#27272a] text-xs text-neutral-900 dark:text-white focus:outline-none"
                >
                  <option value="photo">Foto / Imagen</option>
                  <option value="audio">Audio / Nota de Voz</option>
                  <option value="document">Documento / PDF</option>
                </select>
              </div>

              {/* DETONANTE PROMPT QUESTION */}
              <div className="space-y-2 bg-neutral-50 dark:bg-[#18181d] border border-neutral-200 dark:border-[#27272a] p-4 rounded-xl">
                <label className="text-xs font-bold text-neutral-800 dark:text-neutral-200 flex items-center gap-1.5">
                  <Sparkles className="size-3.5 text-lime-600 dark:text-[#b9fa01]" />
                  ¿Cuándo te gustaría que el agente use este elemento?
                </label>
                <textarea
                  required
                  value={triggerPrompt}
                  onChange={(e) => setTriggerPrompt(e.target.value)}
                  placeholder="Ej: Envia esta foto cuando pregunten por los resultados de Botox..."
                  className="w-full h-20 p-3 rounded-lg bg-white dark:bg-[#141418] border border-neutral-200 dark:border-[#27272a] text-xs text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-lime-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-neutral-100 dark:border-[#22222a]">
                <Button type="button" variant="outline" onClick={() => setIsUploadOpen(false)} className="text-xs rounded-xl cursor-pointer">
                  Cancelar
                </Button>
                <Button type="submit" disabled={isUploading} className="bg-neutral-900 hover:bg-neutral-800 text-white dark:bg-[#b9fa01] dark:hover:bg-[#a3dc01] dark:text-black font-semibold text-xs px-4 py-2 rounded-xl shadow-xs cursor-pointer">
                  {isUploading ? "Guardando..." : "Guardar y Registrar Recurso"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
