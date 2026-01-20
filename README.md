# Blackyak 100 Mountains Tracker

A comprehensive information platform for hikers challenging the **Blackyak 100 Famous Mountains** in South Korea.

![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?logo=tailwindcss)
![Vite](https://img.shields.io/badge/Vite-7.3-646CFF?logo=vite)

## Features

- **100 Famous Mountains List** - Browse all mountains with filtering by region and altitude
- **Mountain Details** - View elevation, location, certification points, and descriptions
- **Trail Maps** - Interactive maps with trail routes for 62 mountains (Leaflet-based)
- **Summit Markers** - Gold markers showing summit positions with elevation data
- **Wikipedia Integration** - Mountain descriptions from Korean Wikipedia (87/99 mountains)
- **Responsive Design** - Mobile-first UI optimized for outdoor use

## Demo

**Live Demo**: [https://frontend-iyx82grvb-daehyub71s-projects.vercel.app](https://frontend-iyx82grvb-daehyub71s-projects.vercel.app)

## Tech Stack

### Frontend
- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Maps**: React-Leaflet + OpenStreetMap
- **State Management**: Zustand + TanStack Query
- **Routing**: React Router v6

### Data Sources
- **Mountain Data**: Blackyak official 100 mountains list
- **Trail Data**: Korea Forest Service trail spatial data (GPX)
- **Descriptions**: Korean Wikipedia REST API
- **Maps**: OpenStreetMap tiles

## Project Structure

```
blackyak-mountain-tracker/
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   └── types/           # TypeScript types
│   └── public/
│       ├── mountain_info/   # Mountain info JSON (99 files)
│       └── trails/          # Trail data JSON (62 files)
├── scripts/                 # Data collection scripts
│   ├── crawl_blackyak_100.py
│   ├── convert_gpx_to_json.py
│   └── fetch_wiki_mountain_info.py
├── data/                    # Raw and processed data
│   └── raw/
│       └── blackyak_100.csv
└── docs/                    # Documentation
```

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/daehyub71/blackyak-mountain-tracker.git
cd blackyak-mountain-tracker

# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Build for Production

```bash
cd frontend
npm run build
```

## Data Collection (Optional)

If you want to regenerate the data:

```bash
cd scripts
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Fetch Wikipedia descriptions
python fetch_wiki_mountain_info.py

# Convert GPX trails to JSON
python convert_gpx_to_json.py
```

## Deployment

This project is configured for Vercel deployment:

```bash
cd frontend
vercel --prod
```

## Screenshots

### Mountain List
Browse 100 famous mountains with filters for region and altitude.

### Mountain Detail
View detailed information including trail maps, summit markers, and descriptions.

### Trail Map
Interactive map showing trail routes with start/end points and summit markers.

## Roadmap

- [ ] User authentication (Supabase)
- [ ] Personal progress tracking
- [ ] Completion photo uploads
- [ ] Weather integration
- [ ] Community features

## License

MIT License

## Acknowledgments

- [Blackyak](https://www.blackyak.com/) for the 100 Famous Mountains challenge
- [Korea Forest Service](https://www.forest.go.kr/) for trail spatial data
- [Korean Wikipedia](https://ko.wikipedia.org/) for mountain descriptions
- [OpenStreetMap](https://www.openstreetmap.org/) for map tiles
