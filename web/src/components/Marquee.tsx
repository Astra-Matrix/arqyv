const ITEMS = [
  "MP4","MKV","AVI","MOV","WMV","WebM","FLAC","MP3","AAC","OGG","OPUS","WAV","AIFF","APE",
  "MKA","ALAC","JPG","PNG","WEBP","HEIC","TIFF","GIF","SVG","BMP","PDF","DOCX","XLSX","PPTX",
  "EPUB","TXT","MD","M4V","3GP","TS","MTS","M2TS","M4A","WMA","OGV","FLV",
];

export default function Marquee() {
  const doubled = [...ITEMS, ...ITEMS];
  return (
    <div className="relative w-full overflow-hidden py-6 select-none"
         style={{ borderTop: "1px solid rgba(255,255,255,0.04)", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
      {/* Fade edges */}
      <div className="absolute inset-y-0 left-0 w-24 z-10 pointer-events-none"
           style={{ background: "linear-gradient(to right, #030305, transparent)" }} />
      <div className="absolute inset-y-0 right-0 w-24 z-10 pointer-events-none"
           style={{ background: "linear-gradient(to left, #030305, transparent)" }} />

      <div className="flex gap-4 w-max animate-slide-left">
        {doubled.map((ext, i) => (
          <span
            key={i}
            className="text-[11px] font-mono font-medium px-2.5 py-1 rounded-md text-white/30 shrink-0"
            style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)" }}
          >
            {ext}
          </span>
        ))}
      </div>
    </div>
  );
}
