# Space Missions Explorer & Analytics System

A Django-based web application for exploring, searching, filtering, visualizing, and generating insights from historical space mission data. Built with a modern 3D glassmorphic UI, Bootstrap 5, and dynamic chart-driven analytics with drill-down capabilities.

## Features

- **3D Glassmorphic UI** - Modern frosted glass cards, backdrop blur, 3D hover effects, smooth animations
- **Sidebar Navigation** - Fixed glassmorphic sidebar with search, theme toggle, and responsive mobile menu
- **Dashboard** - Animated 3D KPI cards, interactive charts, and auto-generated insights
- **Mission Browsing** - Paginated data table with server-side sorting (25 records/page)
- **AJAX Search** - Debounced 300ms search across all columns with instant results and suggestions
- **Advanced Filtering** - Auto-detected filter dropdowns with multi-column AND logic
- **Mission Details** - Glassmorphic detail page with 3D field cards and bookmark support
- **Analytics** - Interactive charts (line, bar, doughnut, stacked bar) with click-to-drill-down
- **Drill-Down** - Dedicated page showing filtered missions for any chart segment
- **Reports** - Modern 3D report pages with KPI cards, insights, column badges
- **Statistics** - 3D stat cards with shine overlay and column-level analysis
- **Data Quality** - Quality score, null analysis, visual indicators with progress bars
- **CSV/Excel Export** - Download full dataset as CSV or Excel
- **Bookmarks** - Save missions with direct links to detail pages
- **Dark/Light Mode** - Theme toggle with localStorage persistence and OS preference detection
- **Responsive Design** - Works on desktop, laptop, tablet, and mobile with collapsible sidebar
- **Auto Dataset Discovery** - Automatically loads all CSV files from `project_dataset/`
- **Data-Driven** - All charts, statistics, and analytics generated dynamically from the actual dataset

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 5.x, Python 3.10+ |
| Architecture | MVT (Model-View-Template) |
| Data Processing | Pandas, NumPy |
| Database | SQLite (Bookmarks, Favorites) |
| Frontend | HTML5, Bootstrap 5.3.2, CSS3, JavaScript |
| Visualization | Chart.js 4.4.1 |
| Icons | Font Awesome 6.5.1 |
| Fonts | Inter (Google Fonts) |
| Caching | Django LocMemCache (600s TTL) |
| UI Design | Glassmorphism with 3D effects |

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd space-missions-explorer
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Place your dataset
Copy CSV files to the `project_dataset/` folder. The system will automatically detect and load them.

### 6. Run the server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Project Structure

```
space-missions-explorer/
├── project_dataset/              # CSV dataset files (auto-scanned)
│   └── Space_Corrected.csv
├── space_missions/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                     # Services, analytics engine, utilities
│   │   ├── services.py           # Dataset loading, caching, search, metadata
│   │   ├── analytics.py          # Chart data, insights, statistics
│   │   ├── context_processors.py # Global template context
│   │   └── management/           # Custom management commands
│   ├── dashboard/                # Home page, bookmarks, API endpoints
│   │   ├── views.py              # Page views + API views
│   │   ├── models.py             # Bookmark model (with link)
│   │   ├── urls.py               # Dashboard routes
│   │   └── templatetags/         # Custom template tags
│   ├── missions/                 # Mission list, detail, search, filter
│   │   ├── views.py              # Mission views + API views
│   │   ├── models.py             # FavoriteMission model
│   │   └── urls.py               # Mission routes
│   ├── analytics/                # Analytics charts, drill-down
│   │   ├── views.py              # Chart views + drill-down API
│   │   └── urls.py               # Analytics routes
│   └── reports/                  # Statistics, data quality, exports
│       ├── views.py              # Report views + export + API
│       └── urls.py               # Report routes
├── templates/                    # HTML templates (Bootstrap 5 + 3D glassmorphic)
│   ├── base.html                 # Base template with sidebar
│   ├── dashboard/                # Home, bookmarks
│   ├── missions/                 # List, detail
│   ├── analytics/                # Analytics, drill-down
│   └── reports/                  # Reports, statistics, data quality
├── static/
│   ├── css/style.css             # Glassmorphic styles + 3D effects + report styles
│   └── js/main.js                # AJAX, charts, search, filters, theme, KPIs
├── SRS_Document.md               # Software Requirements Specification
├── README.md
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## Dataset Requirements

Place CSV files in the `project_dataset/` folder. The system:

1. Automatically scans for all `.csv` files
2. Loads them using Pandas with encoding fallback
3. Detects column types (numeric, categorical, datetime)
4. Auto-generates filters, charts, statistics, and analytics
5. Adapts dashboards and reports dynamically

No code changes required when replacing datasets.

### Dataset Used
- **File**: `Space_Corrected.csv`
- **Records**: 4,324 space missions
- **Columns**: Company Name, Location, Datum, Detail, Status Rocket, Rocket, Status Mission

## Pages

| URL | Description |
|-----|-------------|
| `/` | Dashboard with 3D KPI cards, charts, and insights |
| `/missions/` | Browse all missions with search, filters, and pagination |
| `/missions/detail/<id>/` | Mission detail page with glassmorphic field cards |
| `/analytics/` | Analytics with 8+ interactive charts (click to drill-down) |
| `/analytics/drilldown/<chart_id>/?label=<value>` | Drill-down page for chart segments |
| `/reports/` | Report summary with 3D KPI cards and insights |
| `/reports/statistics/` | Column-level statistics with 3D stat cards |
| `/reports/data-quality/` | Data quality analysis with visual indicators |
| `/reports/export/csv/` | Export full dataset as CSV |
| `/reports/export/excel/` | Export full dataset as Excel |
| `/bookmarks/` | Saved bookmarks with direct mission links |
| `/admin/` | Django admin panel |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats/` | GET | Dashboard KPI statistics |
| `/api/insights/` | GET | Auto-generated insights |
| `/api/suggestions/?q=<query>` | GET | Search suggestions |
| `/api/filters/` | GET | Available filter options |
| `/missions/api/list/` | GET | Paginated, filterable mission data |
| `/missions/api/detail/<id>/` | GET | Single mission details |
| `/analytics/api/<chart_id>/` | GET | Chart data |
| `/analytics/api/<chart_id>/missions/` | GET | Drill-down filtered missions |
| `/reports/api/summary/` | GET | Report summary |
| `/reports/api/statistics/` | GET | Column statistics |
| `/reports/api/quality/` | GET | Data quality report |
| `/bookmark/add/` | POST | Create bookmark with name, link, id |
| `/bookmark/remove/<id>/` | POST | Delete bookmark |

## Performance

- **Server-side pagination** - Only 25 records loaded per request
- **In-memory caching** - DataFrames cached for 600 seconds
- **Debounced search** - 300ms delay prevents excessive API calls
- **Lazy chart loading** - Charts render only when visible (IntersectionObserver)
- **AJAX data loading** - No page refreshes for search, filter, and pagination

## Error Handling

- Missing datasets (shows empty state messages)
- Corrupted CSV files (tries multiple encodings)
- NaT datetime values (graceful handling in date formatting)
- Missing columns (only shows analytics for existing data)

## License

SCD Lab Project - University Academic Use
