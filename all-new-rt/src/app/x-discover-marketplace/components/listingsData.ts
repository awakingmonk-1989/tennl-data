export type CategoryType = "rentals" | "services" | "jobs" | "freelancers" | "buysell";

export interface Listing {
  id: string;
  type: string;
  title: string;
  location: string;
  price: string;
  usp: string;
  tags: string[];
  image: string;
  imageAlt: string;
  aiScore?: number;
  featured?: boolean;
  phone?: string;
  whatsapp?: string;
}

export const listingsData: Record<CategoryType, Listing[]> = {
  rentals: [
  {
    id: "r1",
    type: "2BHK Rental",
    title: "Spacious 2BHK with Garden View & Parking",
    location: "Koramangala 5th Block, Bangalore",
    price: "₹28,000/mo",
    usp: "5-min walk to DPS School · Zero brokerage",
    tags: ["Parking", "Pet OK", "Semi-furnished"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_1b7e03430-1772751062559.png",
    imageAlt: "Bright modern apartment living room with large windows and natural sunlight streaming in",
    aiScore: 97,
    featured: true,
    phone: "+919845001234",
    whatsapp: "919845001234"
  },
  {
    id: "r2",
    type: "1BHK Rental",
    title: "Cosy 1BHK in Gated Community",
    location: "HSR Layout Sector 2, Bangalore",
    price: "₹16,500/mo",
    usp: "24/7 security · Gym & pool included",
    tags: ["Furnished", "Gym", "Metro 800m"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_16cdb4a20-1771892600651.png",
    imageAlt: "Cozy modern studio apartment with warm light tones and minimalist decor",
    aiScore: 93,
    phone: "+919845002345",
    whatsapp: "919845002345"
  },
  {
    id: "r3",
    type: "3BHK Rental",
    title: "Premium 3BHK Near Outer Ring Road",
    location: "Bellandur, Bangalore",
    price: "₹42,000/mo",
    usp: "Modular kitchen · 2 covered parking spots",
    tags: ["Fully furnished", "2 Parking", "Corner unit"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_1563dd40f-1772793493058.png",
    imageAlt: "Spacious bright living room with open plan layout and large windows",
    aiScore: 91,
    phone: "+919845003456",
    whatsapp: "919845003456"
  },
  {
    id: "r4",
    type: "PG / Hostel",
    title: "Premium Co-living for Working Professionals",
    location: "Indiranagar, Bangalore",
    price: "₹12,000/mo",
    usp: "All bills included · Meals available · WiFi 100Mbps",
    tags: ["All-inclusive", "WiFi", "Meals"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_1126be25e-1765223535726.png",
    imageAlt: "Modern co-living common area with bright natural light and comfortable seating",
    aiScore: 88,
    phone: "+919845004567",
    whatsapp: "919845004567"
  },
  {
    id: "r5",
    type: "Office Space",
    title: "Plug-and-Play Office Space for Startups",
    location: "Domlur, Bangalore",
    price: "₹8,500/seat/mo",
    usp: "Flexi desks available · High-speed internet · Meeting rooms",
    tags: ["Flexi", "Meeting rooms", "24/7 access"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_10e98370e-1772521322431.png",
    imageAlt: "Bright modern coworking office with natural light and open desk layout",
    aiScore: 86,
    phone: "+919845005678",
    whatsapp: "919845005678"
  },
  {
    id: "r6",
    type: "Villa Rental",
    title: "Independent Villa with Private Garden",
    location: "Sarjapur Road, Bangalore",
    price: "₹75,000/mo",
    usp: "4BHK · Private pool · Quiet neighbourhood",
    tags: ["Private pool", "4BHK", "Garden"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_145f70c5b-1774177504950.png",
    imageAlt: "Luxury villa exterior with bright white walls, lush garden and blue sky",
    aiScore: 84,
    featured: true,
    phone: "+919845006789",
    whatsapp: "919845006789"
  }],

  services: [
  {
    id: "s1",
    type: "Home Cleaning",
    title: "Priya's Sparkle Home Cleaning Co.",
    location: "HSR Layout & nearby, Bangalore",
    price: "₹799/session",
    usp: "4.9★ · 340 reviews · Same-day booking available",
    tags: ["Verified", "Insured", "Eco-friendly"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_1fdc7d837-1772152005578.png",
    imageAlt: "Clean bright modern kitchen after professional deep cleaning with sunlight",
    aiScore: 96,
    featured: true,
    phone: "+919900001111",
    whatsapp: "919900001111"
  },
  {
    id: "s2",
    type: "Plumbing",
    title: "Ramesh & Sons Expert Plumbers",
    location: "Pan Bangalore",
    price: "₹499 onwards",
    usp: "Available within 2 hours · 1-year service warranty",
    tags: ["Emergency", "Warranty", "Licensed"],
    image: "https://images.unsplash.com/photo-1723810779650-29f5b9856d67",
    imageAlt: "Bright clean bathroom with modern fixtures and white tiles",
    aiScore: 91,
    phone: "+919900002222",
    whatsapp: "919900002222"
  },
  {
    id: "s3",
    type: "Interior Design",
    title: "Studio Aangan — Interior Design & Decor",
    location: "Koramangala, Bangalore",
    price: "₹1,200/sq.ft",
    usp: "End-to-end execution · 3D preview before work begins",
    tags: ["3D Preview", "Turnkey", "5★ rated"],
    image: "https://images.unsplash.com/photo-1722649935747-ea4ea9e80e68",
    imageAlt: "Beautifully designed bright living room with warm tones and modern furniture",
    aiScore: 94,
    phone: "+919900003333",
    whatsapp: "919900003333"
  },
  {
    id: "s4",
    type: "Dog Grooming",
    title: "Pawsome Mobile Dog Grooming",
    location: "HSR, Koramangala, Indiranagar",
    price: "₹699/visit",
    usp: "Comes to your home · All breeds · Stress-free for pets",
    tags: ["Home visit", "All breeds", "Certified"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_16b3a5201-1772134065992.png",
    imageAlt: "Happy golden retriever being groomed in bright clean setting",
    aiScore: 89,
    phone: "+919900004444",
    whatsapp: "919900004444"
  },
  {
    id: "s5",
    type: "Tutoring",
    title: "BrightMinds Home Tutors — Classes 1–12",
    location: "All Bangalore areas",
    price: "₹400/hr",
    usp: "IIT/NIT graduates · Free trial class · All subjects",
    tags: ["IIT tutors", "Free trial", "All subjects"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_187f85c94-1772782290418.png",
    imageAlt: "Bright study room with natural light and student studying at clean desk",
    aiScore: 87,
    phone: "+919900005555",
    whatsapp: "919900005555"
  },
  {
    id: "s6",
    type: "Packers & Movers",
    title: "QuickShift Packers & Movers",
    location: "Pan Bangalore",
    price: "₹3,500 onwards",
    usp: "GPS-tracked vehicles · Zero damage guarantee · Sunday available",
    tags: ["GPS tracked", "Insured", "Sunday OK"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_19979b90d-1775119939977.png",
    imageAlt: "Bright organized moving boxes and professional movers in clean white van",
    aiScore: 85,
    phone: "+919900006666",
    whatsapp: "919900006666"
  }],

  jobs: [
  {
    id: "j1",
    type: "Full-time · Remote",
    title: "Senior Product Designer",
    location: "Fintech Startup · Series B · Remote",
    price: "₹18–28 LPA",
    usp: "3 interview rounds only · Equity offered · Flexible hours",
    tags: ["Remote", "Equity", "Flexible"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_192b32025-1768466339819.png",
    imageAlt: "Bright open-plan creative office with natural light and collaborative workspace",
    aiScore: 95,
    featured: true
  },
  {
    id: "j2",
    type: "Full-time · Hybrid",
    title: "React Frontend Engineer",
    location: "B2B SaaS · Whitefield, Bangalore",
    price: "₹14–22 LPA",
    usp: "Mac provided · Health insurance for family · 30-day joining bonus",
    tags: ["Mac provided", "Family health", "Joining bonus"],
    image: "https://images.unsplash.com/photo-1542546068979-b6affb46ea8f",
    imageAlt: "Bright modern developer workspace with laptop and clean white desk setup",
    aiScore: 92
  },
  {
    id: "j3",
    type: "Full-time · On-site",
    title: "Growth Marketing Manager",
    location: "D2C Brand · Indiranagar, Bangalore",
    price: "₹12–18 LPA",
    usp: "₹2L annual learning budget · Fast-track promotion · Startup perks",
    tags: ["Learning budget", "Fast-track", "D2C"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_1f08960a3-1767641369756.png",
    imageAlt: "Bright marketing team brainstorming in modern office with whiteboards",
    aiScore: 88
  },
  {
    id: "j4",
    type: "Contract · Remote",
    title: "AI/ML Engineer — 6-month contract",
    location: "US-based startup · Full remote",
    price: "$60–80/hr",
    usp: "USD billing · Async-first team · Potential full-time conversion",
    tags: ["USD billing", "Async", "Convert FT"],
    image: "https://images.unsplash.com/photo-1662018111612-e9ad7ee71562",
    imageAlt: "Bright clean tech workspace with AI visualization on screen and natural light",
    aiScore: 90
  },
  {
    id: "j5",
    type: "Part-time · Remote",
    title: "Content Writer — Tech & Finance",
    location: "Content Agency · Fully Remote",
    price: "₹25,000–40,000/mo",
    usp: "Flexible hours · 10 articles/month · By-line credited",
    tags: ["Flexible", "By-line", "Part-time"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_13e5f6f05-1768529075494.png",
    imageAlt: "Bright minimal home office with writer at desk with warm lamp and notebook",
    aiScore: 85
  },
  {
    id: "j6",
    type: "Full-time · On-site",
    title: "Operations Manager — Logistics",
    location: "Logistics Startup · Electronic City, Bangalore",
    price: "₹10–15 LPA",
    usp: "ESOP offered · Canteen facility · 5-day week",
    tags: ["ESOP", "5-day week", "Canteen"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_15f63d3ca-1767958639289.png",
    imageAlt: "Bright modern logistics warehouse with organized shelving and natural light",
    aiScore: 83
  }],

  freelancers: [
  {
    id: "f1",
    type: "UI/UX Designer",
    title: "Sneha Iyer — Product & Brand Designer",
    location: "Bangalore · Works remotely",
    price: "₹2,500/hr",
    usp: "Ex-Swiggy designer · 60+ projects delivered · Figma expert",
    tags: ["Ex-Swiggy", "Figma", "Brand"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_1738914fc-1772156533346.png",
    imageAlt: "Creative professional woman smiling in bright modern studio workspace",
    aiScore: 97,
    featured: true
  },
  {
    id: "f2",
    type: "Full-Stack Developer",
    title: "Karthik Rajan — React & Node.js Expert",
    location: "Chennai · Available remotely",
    price: "₹3,000/hr",
    usp: "8 years experience · SaaS specialist · Available in 3 days",
    tags: ["React", "Node.js", "SaaS"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_18a0e01e6-1763293528821.png",
    imageAlt: "Professional male developer smiling in bright home office environment",
    aiScore: 94
  },
  {
    id: "f3",
    type: "Content Strategist",
    title: "Ananya Mehta — SEO & Content Strategy",
    location: "Mumbai · Remote only",
    price: "₹1,800/hr",
    usp: "Ranked 40+ websites on Page 1 · B2B SaaS specialist",
    tags: ["SEO", "B2B SaaS", "Strategy"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_10ed2b4f6-1768121115938.png",
    imageAlt: "Professional woman content strategist working in bright airy home office",
    aiScore: 91
  },
  {
    id: "f4",
    type: "Video Editor",
    title: "Rohan Dsouza — Reels & YouTube Editor",
    location: "Goa · Remote",
    price: "₹800/video",
    usp: "Avg 2M+ views on client content · 48hr turnaround",
    tags: ["Reels", "YouTube", "48hr delivery"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_18d217be4-1767046744156.png",
    imageAlt: "Creative video editor working on bright monitor in clean studio setup",
    aiScore: 89
  },
  {
    id: "f5",
    type: "Data Analyst",
    title: "Preethi Subramanian — BI & Analytics",
    location: "Hyderabad · Remote",
    price: "₹2,200/hr",
    usp: "Power BI & Tableau expert · Ex-Amazon · Dashboard in 5 days",
    tags: ["Power BI", "Tableau", "Ex-Amazon"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_193f0d14b-1763299878498.png",
    imageAlt: "Professional data analyst woman smiling in bright modern office",
    aiScore: 92
  },
  {
    id: "f6",
    type: "Copywriter",
    title: "Vikram Nair — Performance Copywriter",
    location: "Delhi · Remote",
    price: "₹1,500/hr",
    usp: "₹10Cr+ ad revenue generated for clients · D2C specialist",
    tags: ["Performance", "D2C", "Ad copy"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_13356c809-1768643122132.png",
    imageAlt: "Professional male copywriter working confidently in bright clean workspace",
    aiScore: 88
  }],

  buysell: [
  {
    id: "b1",
    type: "Electronics · Sell",
    title: "MacBook Pro 14\" M3 — Like New",
    location: "Koramangala, Bangalore",
    price: "₹1,35,000",
    usp: "8 months old · Apple warranty till Dec 2025 · Original box",
    tags: ["Warranty", "Original box", "Negotiable"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_17d746289-1767469901251.png",
    imageAlt: "MacBook Pro laptop on clean bright white desk with natural light",
    aiScore: 96,
    featured: true
  },
  {
    id: "b2",
    type: "Furniture · Sell",
    title: "IKEA 3-Seater Sofa — Excellent Condition",
    location: "HSR Layout, Bangalore",
    price: "₹12,500",
    usp: "Bought 1 year ago · Original receipt · Self-pickup only",
    tags: ["IKEA", "Receipt", "1yr old"],
    image: "https://images.unsplash.com/photo-1722247520976-6c2dcf9ec9fd",
    imageAlt: "Modern grey sofa in bright clean living room with natural window light",
    aiScore: 90
  },
  {
    id: "b3",
    type: "Vehicle · Sell",
    title: "Honda Activa 6G — 2022 Model",
    location: "Indiranagar, Bangalore",
    price: "₹68,000",
    usp: "Single owner · 12,000 km only · All documents clear",
    tags: ["Single owner", "Low km", "Docs clear"],
    image: "https://images.unsplash.com/photo-1702369966730-49fa669e66e1",
    imageAlt: "Clean white scooter parked in bright outdoor setting with blue sky",
    aiScore: 93
  },
  {
    id: "b4",
    type: "Books · Sell",
    title: "UPSC Mains Complete Set — 2023 Edition",
    location: "Jayanagar, Bangalore",
    price: "₹3,200",
    usp: "Full set of 28 books · Highlighted & noted · Courier available",
    tags: ["Full set", "Courier", "2023 ed"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_187f85c94-1772782290418.png",
    imageAlt: "Stack of study books on bright clean desk with warm morning light",
    aiScore: 85
  },
  {
    id: "b5",
    type: "Appliance · Sell",
    title: "LG 1.5 Ton 5-Star Inverter AC",
    location: "Whitefield, Bangalore",
    price: "₹28,000",
    usp: "2 years old · Serviced last month · Includes installation",
    tags: ["5-star", "Serviced", "Installation"],
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_1216ba9b0-1773129598887.png",
    imageAlt: "Modern white air conditioner unit on clean bright white wall",
    aiScore: 87
  },
  {
    id: "b6",
    type: "Jewellery · Sell",
    title: "22K Gold Necklace Set — Temple Design",
    location: "Malleshwaram, Bangalore",
    price: "₹1,12,000",
    usp: "BIS hallmarked · Original bill · Valued ₹1.25L",
    tags: ["BIS hallmark", "Original bill", "Temple design"],
    image: "https://images.unsplash.com/photo-1708222170444-a5880c2aa19d",
    imageAlt: "Beautiful gold jewellery necklace on clean white background with soft bright light",
    aiScore: 91
  }]

};
