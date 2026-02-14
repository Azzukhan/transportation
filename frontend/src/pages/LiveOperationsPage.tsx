import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { AnimatedSection } from "@/components/AnimatedSection";
import { PhoneCall, MapPin, Truck, Clock, Camera } from "lucide-react";

type GalleryCategory = "all" | "fleet" | "pickup" | "heavy" | "exhibition";

const galleryItems = [
  { src: "/legacy-images/carousel-1.jpg", title: "Fleet in daily route operation", category: "fleet" as const },
  { src: "/legacy-images/carousel-2.jpg", title: "Road freight operation", category: "heavy" as const },
  { src: "/legacy-images/pic_2.png", title: "Material transport execution", category: "exhibition" as const },
  { src: "/legacy-images/pic_3.png", title: "Pickup team on active job", category: "pickup" as const },
  { src: "/legacy-images/pic_4.png", title: "Cargo truck staging", category: "fleet" as const },
  { src: "/legacy-images/pic_5.png", title: "Site route dispatch", category: "pickup" as const },
  { src: "/legacy-images/pic_7.png", title: "Commercial delivery movement", category: "fleet" as const },
  { src: "/legacy-images/pic_8.png", title: "Industrial transport support", category: "heavy" as const },
  { src: "/legacy-images/pic_9.png", title: "Logistics lane operation", category: "heavy" as const },
  { src: "/legacy-images/pic_10.png", title: "Exhibition pre-start transfer", category: "exhibition" as const },
  { src: "/legacy-images/pic_11.png", title: "Stand material return movement", category: "exhibition" as const },
  { src: "/legacy-images/pic_12.png", title: "Temporary shop material transport", category: "exhibition" as const },
  { src: "/legacy-images/pic_13.png", title: "Project cargo support", category: "heavy" as const },
  { src: "/legacy-images/pic_14.png", title: "Night operations dispatch", category: "fleet" as const },
];

const filters: { label: string; value: GalleryCategory }[] = [
  { label: "All", value: "all" },
  { label: "Fleet", value: "fleet" },
  { label: "Pickup", value: "pickup" },
  { label: "Heavy", value: "heavy" },
  { label: "Exhibition", value: "exhibition" },
];

const metrics = [
  { icon: Truck, label: "Fleet", value: "Daily route movement" },
  { icon: MapPin, label: "Coverage", value: "Local and intercity operations" },
  { icon: PhoneCall, label: "Dispatch", value: "Update on call with customer and driver" },
  { icon: Clock, label: "Timeline", value: "Before-start and close-out support" },
];

const LiveOperationsPage = () => {
  const [filter, setFilter] = useState<GalleryCategory>("all");

  const visibleItems = useMemo(() => {
    if (filter === "all") return galleryItems;
    return galleryItems.filter((item) => item.category === filter);
  }, [filter]);

  const marqueeA = galleryItems.slice(0, 7);
  const marqueeB = galleryItems.slice(7);
  const featured = visibleItems[0] ?? galleryItems[0];

  return (
    <div>
      <section className="relative overflow-hidden bg-hero-gradient py-24">
        <div className="pointer-events-none absolute -top-20 -right-20 h-60 w-60 rounded-full bg-accent/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 -left-20 h-60 w-60 rounded-full bg-accent/10 blur-3xl" />
        <div className="container mx-auto px-4 relative z-10">
          <AnimatedSection>
            <span className="text-accent text-sm font-bold uppercase tracking-wider">Live Operations</span>
            <h1 className="font-display text-4xl md:text-5xl font-bold text-primary-foreground mt-3 mb-4">
              Real Movement <span className="text-accent">On Ground</span>
            </h1>
            <p className="text-primary-foreground/75 text-lg max-w-2xl">
              We currently provide operations updates by call, connect customers directly with drivers, and support communication 24x7.
            </p>
          </AnimatedSection>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {metrics.map((item, i) => (
              <AnimatedSection key={item.label} delay={i * 0.08}>
                <motion.div
                  whileHover={{ y: -4 }}
                  transition={{ type: "spring", stiffness: 280, damping: 20 }}
                  className="bg-card rounded-xl p-6 shadow-card border border-border/50 text-center h-full"
                >
                  <item.icon size={24} className="text-accent mx-auto mb-3" />
                  <div className="font-display text-lg font-bold mb-1">{item.label}</div>
                  <div className="text-sm text-muted-foreground">{item.value}</div>
                </motion.div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      <section className="pb-8 overflow-hidden">
        <div className="space-y-4">
          <motion.div
            animate={{ x: ["0%", "-50%"] }}
            transition={{ duration: 28, repeat: Infinity, ease: "linear" }}
            className="flex gap-4 w-max"
          >
            {[...marqueeA, ...marqueeA].map((item, idx) => (
              <img key={`${item.src}-${idx}`} src={item.src} alt={item.title} className="h-36 w-56 object-cover rounded-xl border border-border/40" />
            ))}
          </motion.div>
          <motion.div
            animate={{ x: ["-50%", "0%"] }}
            transition={{ duration: 26, repeat: Infinity, ease: "linear" }}
            className="flex gap-4 w-max"
          >
            {[...marqueeB, ...marqueeB].map((item, idx) => (
              <img key={`${item.src}-${idx}`} src={item.src} alt={item.title} className="h-36 w-56 object-cover rounded-xl border border-border/40" />
            ))}
          </motion.div>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-4">
          <AnimatedSection className="mb-8">
            <div className="rounded-xl border border-border/50 bg-card p-4 md:p-5">
              <p className="text-sm text-muted-foreground">
                We do not use a live monitoring system at the moment. Our operations team shares delivery updates by call and keeps coordination active 24x7.
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Along with UAE operations, we also support cargo services for Saudi Arabia and Qatar routes.
              </p>
            </div>
          </AnimatedSection>

          <AnimatedSection className="mb-8">
            <div className="flex flex-wrap items-center gap-3">
              {filters.map((item) => (
                <button
                  key={item.value}
                  onClick={() => setFilter(item.value)}
                  className={`px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                    filter === item.value
                      ? "bg-accent text-accent-foreground border-accent"
                      : "bg-card text-muted-foreground border-border hover:text-foreground"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </AnimatedSection>

          <AnimatedSection className="mb-8">
            <div className="relative rounded-2xl overflow-hidden border border-border/50 shadow-card">
              <img src={featured.src} alt={featured.title} className="w-full h-[320px] md:h-[420px] object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
              <div className="absolute bottom-0 left-0 p-6">
                <span className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide bg-accent/90 text-accent-foreground px-3 py-1 rounded-full mb-3">
                  <Camera size={12} /> Live Shot
                </span>
                <h3 className="font-display text-2xl md:text-3xl font-bold text-white">{featured.title}</h3>
              </div>
            </div>
          </AnimatedSection>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {visibleItems.map((item, idx) => (
              <AnimatedSection key={`${item.src}-${idx}`} delay={idx * 0.04}>
                <motion.div
                  whileHover={{ y: -3, scale: 1.01 }}
                  transition={{ type: "spring", stiffness: 280, damping: 18 }}
                  className="bg-card rounded-xl border border-border/50 overflow-hidden shadow-card"
                >
                  <img src={item.src} alt={item.title} className="h-52 w-full object-cover" />
                  <div className="p-4">
                    <p className="text-sm font-medium">{item.title}</p>
                  </div>
                </motion.div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default LiveOperationsPage;
