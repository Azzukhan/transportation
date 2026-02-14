import { Truck } from "lucide-react";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  subtitle?: string;
  tone?: "default" | "light";
}

const sizeMap = {
  sm: { icon: 20, text: "text-lg" },
  md: { icon: 24, text: "text-xl" },
  lg: { icon: 32, text: "text-2xl" },
};

export const Logo = ({ size = "md", subtitle, tone = "default" }: LogoProps) => {
  const s = sizeMap[size];
  return (
    <div className="flex items-center gap-2">
      <div className="bg-accent-gradient rounded-lg p-2 shadow-accent-glow">
        <Truck size={s.icon} className="text-accent-foreground" />
      </div>
      <div>
        <span className={`font-display font-bold ${s.text} ${tone === "light" ? "text-primary-foreground" : "text-foreground"}`}>
          Sikar<span className="text-accent">Cargo</span>
        </span>
        {subtitle && (
          <p className={`text-[10px] uppercase tracking-widest leading-none ${tone === "light" ? "text-primary-foreground/65" : "text-muted-foreground"}`}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
};
