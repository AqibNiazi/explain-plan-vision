import React, { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { Activity, Cpu, FlaskConical, BookOpen, Menu, X } from "lucide-react";
import { useHealth } from "@/hooks/useHealth";
import clsx from "clsx";

const navItems = [
  { to: "/",        label: "Home",     end: true },
  { to: "/analyze", label: "Analyze"             },
  { to: "/memory",  label: "Memory"              },
  { to: "/about",   label: "About"               },
];

export default function Navbar() {
  const { health } = useHealth();
  const [open, setOpen]     = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const isOnline = health?.model_loaded;

  return (
    <nav
      className={clsx(
        "relative z-50 transition-all duration-300",
        scrolled
          ? "backdrop-blur-md border-b border-[var(--border-base)] bg-[rgba(5,8,16,0.85)]"
          : "bg-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-3 group">
          <div className="relative w-9 h-9 flex items-center justify-center border border-[var(--accent-cyan)] bg-[rgba(0,229,255,0.08)] transition-all group-hover:shadow-[var(--glow-cyan)]">
            <FlaskConical size={18} className="text-[var(--accent-cyan)]" />
          </div>
          <div>
            <span className="font-display font-bold text-[var(--text-primary)] text-sm tracking-wide">
              ExplainPlan
            </span>
            <span className="font-display font-bold text-[var(--accent-cyan)] text-sm tracking-wide ml-1">
              Vision
            </span>
          </div>
        </NavLink>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {navItems.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                clsx(
                  "px-4 py-2 font-mono text-xs uppercase tracking-widest transition-all duration-200",
                  isActive
                    ? "text-[var(--accent-cyan)] border-b border-[var(--accent-cyan)]"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                )
              }
            >
              {label}
            </NavLink>
          ))}
        </div>

        {/* Status indicator */}
        <div className="hidden md:flex items-center gap-2 panel px-3 py-1.5">
          <div
            className={clsx(
              "w-2 h-2 rounded-full",
              isOnline
                ? "bg-[var(--accent-green)] shadow-[0_0_6px_var(--accent-green)] animate-pulse"
                : "bg-[var(--text-muted)]"
            )}
          />
          <span className="font-mono text-xs text-[var(--text-secondary)]">
            {isOnline ? `Model Online · v${health?.version ?? "—"}` : "Offline"}
          </span>
        </div>

        {/* Mobile toggle */}
        <button
          className="md:hidden text-[var(--text-secondary)] hover:text-[var(--accent-cyan)] transition-colors"
          onClick={() => setOpen(!open)}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden panel border-t border-[var(--border-base)] px-6 py-4 flex flex-col gap-3">
          {navItems.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                clsx(
                  "font-mono text-xs uppercase tracking-widest py-2 transition-colors",
                  isActive
                    ? "text-[var(--accent-cyan)]"
                    : "text-[var(--text-secondary)]"
                )
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      )}
    </nav>
  );
}
