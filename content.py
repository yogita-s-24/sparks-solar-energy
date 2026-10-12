"""Editable website content.

Keep every statement here factual. Do not add statistics, testimonials,
certifications or project claims unless they are verified.
"""
from datetime import date

VALUE_POINTS = [
    {
        "icon": "plug-zap",
        "title": "Rely less on the grid",
        "text": "Generate a share of your own electricity from sunlight and reduce your dependence on conventional power.",
    },
    {
        "icon": "trending-down",
        "title": "Plan energy costs for the long term",
        "text": "Make a considered, long-term decision about electricity costs, based on how you actually use power.",
    },
    {
        "icon": "leaf",
        "title": "Choose a cleaner future",
        "text": "Use renewable energy from your own roof or land and contribute to a more sustainable tomorrow.",
    },
]

SOLUTIONS = [
    {
        "slug": "residential",
        "number": "01",
        "icon": "house",
        "title": "Residential Solar",
        "summary": "Rooftop solar solutions for homes, designed around household energy requirements and available roof space.",
        "image": "images/stock/residential-home.webp",
        "image_alt": "Detached house with blue rooftop solar panels in bright sunshine",
        "points": [
            "Review of recent electricity bills and household consumption",
            "Assessment of shade-free roof area, orientation and roof condition",
            "Guidance on on-grid, off-grid or hybrid system options",
            "Support with documentation for applicable schemes, where eligible",
        ],
    },
    {
        "slug": "agricultural",
        "number": "02",
        "icon": "tractor",
        "title": "Agricultural Solar",
        "summary": "Solar energy options for agricultural applications, assessing requirements for pumps and other farm electricity needs.",
        "image": "images/stock/agricultural-array.webp",
        "image_alt": "Ground-mounted solar panel array beside green orchard trees",
        "points": [
            "Assessment of pump rating, water source and daily water requirement",
            "Solar pumping options for irrigation needs",
            "Planning for other farm electricity loads",
            "Information on agricultural solar schemes, subject to current eligibility",
        ],
    },
    {
        "slug": "commercial",
        "number": "03",
        "icon": "building-2",
        "title": "Commercial Solar",
        "summary": "Solar energy solutions for shops, offices, commercial buildings and businesses, focused on energy planning and long-term operating costs.",
        "image": "images/stock/commercial-rooftop.webp",
        "image_alt": "Rows of solar panels on a flat commercial rooftop with a city skyline",
        "points": [
            "Review of daytime load profile and electricity tariff",
            "Rooftop or ground-mounted layout planning",
            "System options matched to operating hours and budget",
            "Ongoing maintenance planning through AMC services",
        ],
    },
]

BENEFITS = [
    {
        "icon": "indian-rupee",
        "title": "Potential to reduce electricity bills",
        "text": "Solar can lower what you pay for grid electricity. How much depends on your usage, tariff and system design, which is why we start with your actual bills.",
    },
    {
        "icon": "sun-medium",
        "title": "More renewable energy",
        "text": "Every unit generated on your roof is a unit of clean, renewable electricity used by your home, farm or business.",
    },
    {
        "icon": "gauge",
        "title": "Potential long-term cost benefits",
        "text": "A well-planned system can help you manage energy costs over the long run. We explain the factors that affect this clearly, without guarantees.",
    },
    {
        "icon": "sliders-horizontal",
        "title": "Tailored to your consumption",
        "text": "The system is planned around your electricity consumption, available space and budget — not a one-size-fits-all package.",
    },
    {
        "icon": "recycle",
        "title": "A more sustainable future",
        "text": "Generating your own clean energy helps reduce reliance on conventional sources for your family, farm and community.",
    },
]

STEPS = [
    {
        "icon": "clipboard-list",
        "title": "Share Your Requirements",
        "text": "Call, WhatsApp or fill a short form. Tell us about your property and your electricity bills.",
    },
    {
        "icon": "scan-search",
        "title": "Assess Your Site and Energy Needs",
        "text": "We review your consumption and look at roof or land area, shade and site conditions.",
    },
    {
        "icon": "file-text",
        "title": "Get a Suitable Solar Proposal",
        "text": "Receive a proposal with the recommended system type and the details explained clearly.",
    },
    {
        "icon": "calendar-check",
        "title": "Plan Your Installation",
        "text": "Once you are comfortable, we plan the installation schedule and next steps with you.",
    },
]

# System types and services listed on the business's own promotional material.
SYSTEM_TYPES = [
    {
        "icon": "plug-zap",
        "title": "On-Grid Solar System",
        "text": "Connected to the electricity grid. Solar power is used first, and surplus may be exported under your distribution company's applicable metering rules. Typically no batteries.",
    },
    {
        "icon": "battery-charging",
        "title": "Off-Grid Solar System",
        "text": "Works independently of the grid with battery storage. Suited to locations where grid supply is unavailable or unreliable.",
    },
    {
        "icon": "zap",
        "title": "Hybrid Solar System",
        "text": "Combines grid connection with battery backup, so essential loads can keep running during power cuts.",
    },
]

SERVICES = [
    {"icon": "droplets", "title": "Solar Water Heating", "text": "Solar water heaters for homes and buildings that need hot water every day."},
    {"icon": "sprout", "title": "Solar Pumping Systems", "text": "Solar-powered pumping for irrigation and farm water needs."},
    {"icon": "wrench", "title": "AMC & Maintenance", "text": "Annual maintenance and servicing to help keep your system in good working order."},
]

# Package prices supplied by the business (including GST and installation).
# "subsidy" is the government subsidy amount for the package (0 if none). The
# customer pays the price plus this amount at installation, and the subsidy is
# credited back once approved, so their final cost is the package price.
PRICING = [
    {
        "slug": "residential",
        "icon": "plug-zap",
        "title": "3 kW On-Grid System",
        "summary": "Grid-connected rooftop solar for homes. No batteries.",
        "unit": "",
        "subsidy": 78000,
        "tiers": [("Standard", 102000), ("Premium", 112000)],
    },
    {
        "slug": "residential",
        "icon": "battery-charging",
        "title": "3 kW Hybrid System",
        "summary": "Grid connection with battery backup for power cuts.",
        "unit": "",
        "subsidy": 78000,
        "tiers": [("Standard", 230000), ("Premium", 250000)],
    },
    {
        "slug": "commercial",
        "icon": "building-2",
        "title": "Commercial Solar",
        "summary": "For shops, offices and industries. Priced per kW of installed capacity.",
        "unit": "/kW",
        "subsidy": 0,
        "tiers": [("Standard", 50000), ("Premium", 55000)],
    },
]

# PM Surya Ghar: Muft Bijli Yojana (central subsidy for residential rooftop solar).
# Figures supplied by the business; re-check https://pmsuryaghar.gov.in when the
# scheme changes. The deadline notice hides itself after END_DATE.
SUBSIDY = {
    "scheme": "PM Surya Ghar: Muft Bijli Yojana",
    "end_date": date(2027, 3, 31),
    "rates": [
        ("Up to 2 kW", "₹30,000 per kW", "₹60,000 for a 2 kW system"),
        ("Additional capacity up to 3 kW", "₹18,000 per kW", "₹78,000 for a 3 kW system"),
        ("Systems larger than 3 kW", "₹78,000", "Maximum cap for residential households"),
        ("Housing societies (GHS / RWA)", "₹18,000 per kW", "Common facilities, up to 500 kW"),
    ],
}

SUBSIDY_STEPS = [
    {"icon": "wallet", "title": "Pay at installation", "text": "You pay the package price plus the applicable government subsidy amount."},
    {"icon": "file-text", "title": "Subsidy is processed", "text": "The subsidy claim is processed under the government scheme for eligible systems."},
    {"icon": "badge-indian-rupee", "title": "Subsidy credited back", "text": "Once approved, the subsidy is credited to you, so your final cost is the package price."},
]

# Components used in SPARKS SOLAR ENERGY systems (as supplied by the business).
COMPONENTS = [
    {"icon": "grid-2x2", "name": "Solar PV Modules", "spec": "Waaree / Adani"},
    {"icon": "plug-zap", "name": "Grid-Tied Inverter", "spec": "Polycab string inverter with built-in Wi-Fi monitoring"},
    {"icon": "construction", "name": "Module Mounting Structure", "spec": "Apollo GI pipe structure, 3\" × 3\" heavy duty, wind-rated"},
    {"icon": "cable", "name": "AC Cabling", "spec": "Polycab heavy multi-core armoured AC cable, as required"},
    {"icon": "cable", "name": "DC Cabling", "spec": "Polycab UV-resistant, halogen-free DC solar cable, as required"},
    {"icon": "zap", "name": "Earthing & Lightning Arrester", "spec": "Heavy maintenance-free chemical earthing + copper LA"},
    {"icon": "shield-check", "name": "Protection & Switchgear", "spec": "ACDB / DCDB with Type II surge protection devices (SPD) & MCBs"},
]

# Commitments stated on the business's promotional material.
COMMITMENTS = [
    {"icon": "shield-check", "title": "Quality products", "text": "We focus on dependable components chosen for your requirement."},
    {"icon": "hard-hat", "title": "Expert installation", "text": "Installation planned and carried out by a trained technical team."},
    {"icon": "heart-handshake", "title": "After-sales support", "text": "Support and maintenance services after your system is installed."},
]

# Team as listed on the business flyer. Confirm spellings before launch.
TEAM = [
    {"name": "Prasad Gadakh", "role": "Solar Technician"},
    {"name": "Sanket Chavan", "role": "Civil Engineer"},
    {"name": "Krushna Dethe", "role": "Electrical Engineer"},
]

FAQS = [
    {
        "q": "How does a rooftop solar system work?",
        "a": "Solar panels convert sunlight into direct current (DC) electricity. An inverter converts it into alternating current (AC), which your lights, fans, pumps and appliances use. In an on-grid system, surplus electricity may be exported to the grid under your electricity distribution company's applicable metering arrangement. Off-grid systems store energy in batteries, and hybrid systems combine both.",
    },
    {
        "q": "Is solar suitable for my home?",
        "a": "It depends on a few practical things: shade-free roof area, roof condition and orientation, your monthly electricity consumption and your budget. Share a recent electricity bill and some details about your roof, and we can tell you whether solar is a sensible option for you.",
    },
    {
        "q": "Can farmers use solar energy?",
        "a": "Yes. Solar can be used for agricultural applications such as water pumping and other farm electricity needs. Suitability depends on factors like the pump rating, water source, depth, daily water requirement and available land. We assess these before recommending a system.",
    },
    {
        "q": "How do I determine the right system size?",
        "a": "System size is based mainly on your electricity consumption (units/kWh across recent bills, ideally for a full year), the shade-free area available, your sanctioned load and the rules of your distribution company. We calculate a suitable size after reviewing these details. The online estimator on this website is only illustrative.",
    },
    {
        "q": "How can I request a quotation?",
        "a": "Fill in the enquiry form, call us on +91 9356806280 or send a WhatsApp message. Please keep a recent electricity bill handy. It helps us understand your requirement quickly.",
    },
    {
        "q": "How much does a solar system cost?",
        "a": "Our 3 kW on-grid system is ₹1,02,000 (Standard) or ₹1,12,000 (Premium), and our 3 kW hybrid system is ₹2,30,000 (Standard) or ₹2,50,000 (Premium). For these 3 kW systems you also pay the ₹78,000 government subsidy amount at installation, which is credited back once approved for eligible households, so your final cost is the package price. Commercial systems are ₹50,000 (Standard) or ₹55,000 (Premium) per kW. All prices include GST and installation. We confirm your exact quotation after a site survey.",
        "links": [("See pricing and components", "/solutions#pricing")],
    },
    {
        "q": "Are government subsidies available?",
        "a": "Yes. Under PM Surya Ghar: Muft Bijli Yojana, eligible residential households can receive ₹30,000 for a 1 kW system, ₹60,000 for a 2 kW system and ₹78,000 (the maximum) for 3 kW and above. Group housing societies and resident welfare associations can receive ₹18,000 per kW for common facilities, up to 500 kW. The current phase of the scheme runs until 31 March 2027. For farms, PM-KUSUM covers agricultural solar. Eligibility is decided under the scheme rules, so please check the official portal. We will explain what applies to your home.",
        "links": [("PM Surya Ghar portal", "https://pmsuryaghar.gov.in"), ("Ministry of New and Renewable Energy", "https://mnre.gov.in")],
    },
    {
        "q": "Do you provide maintenance after installation?",
        "a": "Yes. AMC (annual maintenance contract) and maintenance services are part of what we offer. Ask us about the scope and frequency that suits your system.",
    },
]

# Demonstration gallery. Replace with genuine project photos when available:
# put files in static/images/projects/ and set "demo": False for each item.
GALLERY = [
    {"src": "images/stock/neighbourhood-rainbow.webp", "alt": "Homes with rooftop solar panels under a rainbow", "category": "residential", "caption": "Rooftop solar on homes", "size": "wide"},
    {"src": "images/stock/aerial-commercial.webp", "alt": "Aerial view of solar panels covering a large commercial roof", "category": "commercial", "caption": "Large commercial rooftop", "size": "tall"},
    {"src": "images/stock/rural-home-rooftop.webp", "alt": "Aerial view of a rural house with solar panels on its roof, surrounded by farmland", "category": "residential", "caption": "Rooftop solar on a rural home", "size": "tall"},
    {"src": "images/stock/aerial-field.webp", "alt": "Aerial view of solar panels arranged on green grassland", "category": "agricultural", "caption": "Ground-mounted array on open land", "size": "normal"},
    {"src": "images/stock/commercial-sunset.webp", "alt": "Solar panels in front of a commercial building at sunset", "category": "commercial", "caption": "Commercial site at sunset", "size": "wide"},
    {"src": "images/stock/panel-grass.webp", "alt": "Long ground-mounted solar panel row on a grass field under blue sky", "category": "agricultural", "caption": "Ground-mounted solar on farmland", "size": "wide"},
    {"src": "images/stock/pole-mounted-panel.webp", "alt": "Pole-mounted solar panel powering equipment in a rural landscape", "category": "agricultural", "caption": "Stand-alone solar for remote equipment", "size": "normal"},
]
for _item in GALLERY:
    _item.setdefault("demo", True)

GALLERY_FILTERS = [
    ("all", "All"),
    ("residential", "Residential"),
    ("commercial", "Commercial"),
    ("agricultural", "Agricultural"),
]

# Credits for the demonstration photographs (Unsplash Licence).
IMAGE_CREDITS_URL = "https://unsplash.com/license"
