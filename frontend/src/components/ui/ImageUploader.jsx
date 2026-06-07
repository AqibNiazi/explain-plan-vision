import React, { useRef, useState } from "react";
import { UploadCloud, X, ImageIcon } from "lucide-react";
import clsx from "clsx";

const ACCEPT = "image/jpeg,image/png,image/webp";
const MAX_MB = 10;

export default function ImageUploader({ onFile, disabled }) {
  const [preview, setPreview]   = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      alert("Please upload an image file (JPG, PNG, WebP).");
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      alert(`File too large. Max ${MAX_MB} MB.`);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    onFile(file);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  const clear = (e) => {
    e.stopPropagation();
    setPreview(null);
    onFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div
      className={clsx("dropzone relative rounded-none", dragging && "active")}
      style={{ minHeight: 220 }}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="hidden"
        disabled={disabled}
        onChange={(e) => handleFile(e.target.files?.[0])}
      />

      {preview ? (
        <div className="relative w-full h-full flex items-center justify-center p-4">
          <img
            src={preview}
            alt="Leaf preview"
            className="max-h-64 max-w-full object-contain"
            style={{ imageRendering: "auto" }}
          />
          {!disabled && (
            <button
              onClick={clear}
              className="absolute top-3 right-3 w-7 h-7 flex items-center justify-center"
              style={{
                background: "var(--bg-root)",
                border: "1px solid var(--accent-red)",
                color: "var(--accent-red)",
              }}
            >
              <X size={14} />
            </button>
          )}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-4 py-14 px-6 text-center">
          <div
            className="w-16 h-16 flex items-center justify-center"
            style={{
              border: "1px solid var(--border-bright)",
              background: "rgba(0,229,255,0.05)",
            }}
          >
            <UploadCloud size={28} style={{ color: "var(--accent-cyan)" }} />
          </div>
          <div>
            <p className="font-mono text-sm" style={{ color: "var(--text-primary)" }}>
              Drop a leaf image here
            </p>
            <p className="font-mono text-xs mt-1" style={{ color: "var(--text-muted)" }}>
              or click to browse — JPG · PNG · WebP · max {MAX_MB} MB
            </p>
          </div>
          <div
            className="flex items-center gap-2 px-3 py-1"
            style={{ border: "1px dashed var(--border-dim)" }}
          >
            <ImageIcon size={11} style={{ color: "var(--text-muted)" }} />
            <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
              PlantVillage compatible · 15 disease classes
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
