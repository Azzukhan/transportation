export type ServiceItem = {
  slug: string;
  title: string;
  subtitle: string;
  summary: string;
  description: string;
  image: string;
  capacity: string;
  bestFor: string[];
  highlights: string[];
};

export type GalleryItem = {
  src: string;
  title: string;
  category: "fleet" | "pickup" | "exhibition" | "heavy";
};

export const serviceItems: ServiceItem[] = [
  {
    slug: "one-ton-pickup",
    title: "1 Ton Pickup Service",
    subtitle: "Fast local and inter-city pickup support",
    summary: "Light commercial cargo movement for daily distribution and urgent business dispatch.",
    description:
      "Our 1-ton pickup service is ideal for compact freight that requires same-day handling. It supports retail deliveries, supplier dispatch, maintenance cargo, and daily replenishment through disciplined pickup scheduling.",
    image: "/legacy-images/1_ton.png",
    capacity: "Up to 1 ton",
    bestFor: ["Daily goods delivery", "Retail replenishment", "Urgent parts movement"],
    highlights: ["Same-day dispatch windows", "Professional loading support", "Clean and tracked movement"],
  },
  {
    slug: "three-ton-pickup",
    title: "3 Ton Pickup Service",
    subtitle: "Balanced volume and speed",
    summary: "Mid-size freight solution for branch transfers and structured B2B route plans.",
    description:
      "The 3-ton pickup service gives businesses the right mix of capacity and agility. It is widely used for wholesale transfers, office movement support, and route-level scheduled distribution across the UAE.",
    image: "/legacy-images/3_ton.png",
    capacity: "Up to 3 tons",
    bestFor: ["Wholesale movement", "Branch stock transfer", "Scheduled route operations"],
    highlights: ["Planned slot-based pickups", "On-time route commitment", "Reliable city-to-city handling"],
  },
  {
    slug: "seven-ton-service",
    title: "7 Ton Service",
    subtitle: "High-capacity commercial movement",
    summary: "Operationally strong option for industrial material and large shipment batches.",
    description:
      "Our 7-ton fleet is built for heavy daily operations where stability and load discipline matter. It is suitable for warehouse distribution, project cargo support, and repeat B2B movement with practical scheduling.",
    image: "/legacy-images/7_ton.png",
    capacity: "Up to 7 tons",
    bestFor: ["Industrial supply movement", "Warehouse dispatch", "Bulk cargo transfer"],
    highlights: ["Reliable heavy-route execution", "Experienced operations coordination", "Consistent turnaround commitments"],
  },
  {
    slug: "ten-ton-pickup",
    title: "10 Ton Pickup Service",
    subtitle: "Heavy-duty freight support",
    summary: "Large-batch movement for project sites and high-volume distribution needs.",
    description:
      "The 10-ton pickup service is designed for major logistics movement, including oversized delivery plans and repeated high-volume routes. Teams are assigned based on cargo profile and destination requirements.",
    image: "/legacy-images/10_ton_pickup.png",
    capacity: "Up to 10 tons",
    bestFor: ["Project cargo movement", "Large stock transfer", "Heavy distribution plans"],
    highlights: ["High-volume carrying power", "Route and timing control", "Safe handling workflow"],
  },
  {
    slug: "truck-freight",
    title: "Truck Freight",
    subtitle: "Long-haul and large-volume transport",
    summary: "Purpose-built truck operations for major cargo movement with route discipline.",
    description:
      "Our truck freight operations support long-distance and high-volume transport requirements across the UAE. This service is used for contracted business routes, consolidated freight movement, and enterprise-level logistics continuity.",
    image: "/legacy-images/Truck.jfif",
    capacity: "Custom by route and load type",
    bestFor: ["Long-haul delivery", "Enterprise logistics contracts", "Large volume consolidation"],
    highlights: ["Dedicated route planning", "Dispatch control and updates", "Commercial-grade delivery reliability"],
  },
  {
    slug: "exhibition-logistics",
    title: "Exhibition Logistics",
    subtitle: "Pre- and post-exhibition material transport",
    summary: "Transport support for exhibition materials before event start and after event close-out.",
    description:
      "We handle transport before exhibitions begin and after exhibitions close. This includes stand materials, construction wood items, temporary-shop dismantled materials, and related assets. We do not provide lifting operations.",
    image: "/legacy-images/pic_12.png",
    capacity: "Based on exhibition scope",
    bestFor: [
      "Pre-event material delivery",
      "Post-event return and clearance transport",
      "Wood and temporary structure material movement",
    ],
    highlights: [
      "No lifting operations included",
      "Time-critical venue schedule support",
      "Structured pickup and return dispatch",
    ],
  },
];

export const operationGallery: GalleryItem[] = [
  { src: "/legacy-images/carousel-1.jpg", title: "Fleet in daily route operation", category: "fleet" },
  { src: "/legacy-images/carousel-2.jpg", title: "Road freight operation", category: "heavy" },
  { src: "/legacy-images/pic_2.png", title: "Material transport execution", category: "exhibition" },
  { src: "/legacy-images/pic_3.png", title: "Pickup team on active job", category: "pickup" },
  { src: "/legacy-images/pic_4.png", title: "Cargo truck staging", category: "fleet" },
  { src: "/legacy-images/pic_5.png", title: "Site route dispatch", category: "pickup" },
  { src: "/legacy-images/pic_7.png", title: "Commercial delivery movement", category: "fleet" },
  { src: "/legacy-images/pic_8.png", title: "Industrial transport support", category: "heavy" },
  { src: "/legacy-images/pic_9.png", title: "Logistics lane operation", category: "heavy" },
  { src: "/legacy-images/pic_10.png", title: "Exhibition pre-start material transfer", category: "exhibition" },
  { src: "/legacy-images/pic_11.png", title: "Stand material return movement", category: "exhibition" },
  { src: "/legacy-images/pic_12.png", title: "Temporary shop material transport", category: "exhibition" },
  { src: "/legacy-images/pic_13.png", title: "Project cargo support", category: "heavy" },
  { src: "/legacy-images/pic_14.png", title: "Night operations dispatch", category: "fleet" },
];

export const trustPoints = [
  "Door-to-door cargo movement across UAE",
  "Dedicated operations communication",
  "Practical response times for urgent dispatch",
  "Commercial-grade reliability for repeat business",
];
