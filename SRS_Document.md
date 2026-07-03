# Software Requirements Specification (SRS)

## Space Missions Explorer

---

| Field | Detail |
|---|---|
| **Document Title** | Software Requirements Specification |
| **Project Name** | Space Missions Explorer |
| **Version** | 3.0 |
| **Date** | July 5, 2026 |
| **Prepared By** | Mehran Khan, Monum Zahra |
| **Course** | Software Construction and Design (SCD Lab) |
| **Start Date** | June 25, 2026 |
| **Completion Date** | July 5, 2026 |

---

## Table of Contents

1. Introduction
2. Overall Description
3. Functional Requirements
4. Non-Functional Requirements
5. Business Requirements
6. User Requirements
7. System Requirements
8. User Stories
9. Use Cases
10. UML Diagrams
11. Data Dictionary
12. External Interface Requirements
13. Glossary

---

## 1. Introduction

### 1.1 Purpose

This document specifies the complete software requirements for the **Space Missions Explorer** application. It serves as a comprehensive reference for the development team, stakeholders, and evaluators to understand the system's functionality, constraints, and design decisions.

### 1.2 Scope

Space Missions Explorer is a web-based analytics dashboard that enables users to explore, search, filter, analyze, and visualize historical space mission data. The application features a modern 3D glassmorphic UI with sidebar navigation, loads mission data from CSV datasets, and provides dynamic, data-driven analytics including interactive charts with drill-down capabilities.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|---|---|
| SRS | Software Requirements Specification |
| MVT | Model-View-Template (Django architecture pattern) |
| AJAX | Asynchronous JavaScript and XML |
| API | Application Programming Interface |
| CSV | Comma-Separated Values |
| KPI | Key Performance Indicator |
| UI/UX | User Interface / User Experience |
| ORM | Object-Relational Mapping |
| CDN | Content Delivery Network |
| Drill-Down | Clicking a chart element to view filtered underlying data |
| Glassmorphism | UI design trend using blur effects and transparency |
| 3D Effects | Visual depth created through transforms, shadows, and perspective |

### 1.4 References

- Django 5.x Documentation (https://docs.djangoproject.com/)
- Bootstrap 5 Documentation (https://getbootstrap.com/)
- Chart.js Documentation (https://www.chartjs.org/)
- Pandas Documentation (https://pandas.pydata.org/)

---

## 2. Overall Description

### 2.1 Product Perspective

Space Missions Explorer is a standalone web application built using the Django framework following the MVT (Model-View-Template) architectural pattern. It features a fixed glassmorphic sidebar navigation, Bootstrap 5 for UI components, and Chart.js for data visualization with 3D glassmorphic styling throughout.

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|   Web Browser    |<--->|  Django Server   |<--->|   SQLite DB      |
|   (Bootstrap 5   |     |  (Python 3.14)  |     |   (Bookmarks/    |
|    3D Glassmorphic|    |  MVT Pattern     |     |    Favorites)    |
|    Sidebar Nav)   |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                                |
                         +------v------+
                         |             |
                         |  Pandas     |
                         |  (CSV Data) |
                         |  Cached 600s|
                         |             |
                         +-------------+
```

### 2.2 Product Functions

1. **Dashboard** - 3D KPI cards, interactive charts, and auto-generated insights
2. **Sidebar Navigation** - Fixed glassmorphic sidebar with search, theme toggle, responsive mobile menu
3. **Mission Browsing** - Paginated data table with server-side sorting (25 records/page)
4. **Search** - Real-time AJAX search across all columns with debouncing
5. **Filtering** - Dynamic multi-column filtering with auto-detected options
6. **Analytics** - Interactive charts with click-to-drill-down to related missions
7. **Drill-Down** - Dedicated page showing filtered missions for any chart segment
8. **Reports** - 3D glassmorphic report pages with KPI cards and insights
9. **Statistics** - 3D stat cards with shine overlay and column analysis
10. **Data Quality** - Quality score, null analysis, visual indicators
11. **Data Export** - CSV and Excel export
12. **Bookmarks** - Save missions with direct links to detail pages
13. **Theme Switching** - Dark/light mode with OS preference detection

### 2.3 User Classes

| User Type | Description | Technical Level |
|---|---|---|
| **Data Analyst** | Explores mission data, applies filters, exports reports | Medium |
| **Student/Researcher** | Studies space mission trends and patterns | Low-Medium |
| **General User** | Browses missions, views charts and insights | Low |

### 2.4 Operating Environment

- **Server-side**: Python 3.14, Django 5.x, SQLite
- **Client-side**: Modern web browser (Chrome, Firefox, Safari, Edge)

### 2.5 Design Constraints

- Django MVT architecture
- Bootstrap 5 for UI components
- Glassmorphic CSS with 3D effects
- All analytics generated dynamically from dataset
- Fixed sidebar navigation (no top navbar)

---

## 3. Functional Requirements

### 3.1 Dashboard (FR-DASH)

| ID | Requirement | Priority |
|---|---|---|
| FR-DASH-01 | Display total mission count as 3D KPI card | High |
| FR-DASH-02 | Display successful mission count | High |
| FR-DASH-03 | Display failed mission count | High |
| FR-DASH-04 | Display overall success rate percentage | High |
| FR-DASH-05 | Display total unique agencies count | Medium |
| FR-DASH-06 | Display total unique launch sites count | Medium |
| FR-DASH-07 | Render "Missions Per Year" line chart | High |
| FR-DASH-08 | Render "Mission Status" doughnut chart | High |
| FR-DASH-09 | Render "Top Agencies" bar chart | Medium |
| FR-DASH-10 | Render "Success Rate Trend" line chart | Medium |
| FR-DASH-11 | Auto-generate data-driven insights | High |
| FR-DASH-12 | KPI values animate on page load | Low |
| FR-DASH-13 | All charts clickable for drill-down | High |

### 3.2 Navigation (FR-NAV)

| ID | Requirement | Priority |
|---|---|---|
| FR-NAV-01 | Fixed left sidebar navigation | High |
| FR-NAV-02 | Highlight active page in sidebar | High |
| FR-NAV-03 | Collapsible on mobile with hamburger menu | High |
| FR-NAV-04 | Search input and theme toggle in sidebar | Medium |
| FR-NAV-05 | Overlay content on mobile with backdrop | Medium |

### 3.3 Missions (FR-MISS)

| ID | Requirement | Priority |
|---|---|---|
| FR-MISS-01 | Paginated data table (25 records/page) | High |
| FR-MISS-02 | Server-side pagination with Prev/Next | High |
| FR-MISS-03 | Column sorting (ascending/descending) | High |
| FR-MISS-04 | Mission detail page on row click | High |
| FR-MISS-05 | Display all columns for selected mission | Medium |
| FR-MISS-06 | Bookmark functionality on detail page | Medium |

### 3.4 Search (FR-SRCH)

| ID | Requirement | Priority |
|---|---|---|
| FR-SRCH-01 | Global search in sidebar | High |
| FR-SRCH-02 | Table-level search on missions page | High |
| FR-SRCH-03 | Debounce search by 300ms | Medium |
| FR-SRCH-04 | Search across all string columns | High |
| FR-SRCH-05 | Case-insensitive search | High |
| FR-SRCH-06 | Search suggestions while typing | Medium |
| FR-SRCH-07 | Highlight matching text | Low |
| FR-SRCH-08 | Ctrl+K shortcut for search focus | Low |

### 3.5 Filtering (FR-FILT)

| ID | Requirement | Priority |
|---|---|---|
| FR-FILT-01 | Auto-detect available filter columns | High |
| FR-FILT-02 | Only show filters for existing columns | High |
| FR-FILT-03 | Support multiple simultaneous filters | High |
| FR-FILT-04 | Display active filter badges | Medium |
| FR-FILT-05 | Remove individual filters by clicking badge | Medium |
| FR-FILT-06 | "Clear All" button to reset filters | Medium |
| FR-FILT-07 | Filters combine with AND logic | High |

### 3.6 Analytics (FR-ANAL)

| ID | Requirement | Priority |
|---|---|---|
| FR-ANAL-01 | Display 8 interactive charts | High |
| FR-ANAL-02 | Every chart segment clickable | High |
| FR-ANAL-03 | Click navigates to drill-down page | High |
| FR-ANAL-04 | Charts lazy-loaded via IntersectionObserver | Medium |

### 3.7 Drill-Down (FR-DRIL)

| ID | Requirement | Priority |
|---|---|---|
| FR-DRIL-01 | Dedicated drill-down page per chart | High |
| FR-DRIL-02 | Render same chart with click handlers | Medium |
| FR-DRIL-03 | Show filtered missions for selected segment | High |
| FR-DRIL-04 | Paginated drill-down results | High |
| FR-DRIL-05 | Dynamic filtering via chart clicks | High |

### 3.8 Reports (FR-RPTS)

| ID | Requirement | Priority |
|---|---|---|
| FR-RPTS-01 | 3D KPI cards for dataset summary | Medium |
| FR-RPTS-02 | Auto-generated insights | Medium |
| FR-RPTS-03 | CSV export | High |
| FR-RPTS-04 | Excel export | High |
| FR-RPTS-05 | 3D stat cards for column statistics | Medium |
| FR-RPTS-06 | Visual quality indicators | Medium |
| FR-RPTS-07 | Modern 3D glassmorphic UI | Low |

### 3.9 Theme (FR-THME)

| ID | Requirement | Priority |
|---|---|---|
| FR-THME-01 | Dark mode (default) | High |
| FR-THME-02 | Light mode | High |
| FR-THME-03 | Persist preference in localStorage | Medium |
| FR-THME-04 | Detect OS preference | Low |

### 3.10 Bookmarks (FR-BKMK)

| ID | Requirement | Priority |
|---|---|---|
| FR-BKMK-01 | Save missions as bookmarks | Medium |
| FR-BKMK-02 | Store actual mission name | High |
| FR-BKMK-03 | Store direct link to detail page | High |
| FR-BKMK-04 | Show clickable links on bookmarks page | Medium |
| FR-BKMK-05 | Allow removing bookmarks | Medium |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-PERF-01 | Initial page load | < 3 seconds |
| NFR-PERF-02 | AJAX data load | < 1 second |
| NFR-PERF-03 | Search debounce | 300ms |
| NFR-PERF-04 | Chart render | < 2 seconds |
| NFR-PERF-05 | Pagination | 25 records/page |
| NFR-PERF-06 | Caching | 600s TTL |
| NFR-PERF-07 | Lazy chart loading | IntersectionObserver |

### 4.2 Usability

| ID | Requirement |
|---|---|
| NFR-USE-01 | Bootstrap 5 components |
| NFR-USE-02 | Responsive on all devices |
| NFR-USE-03 | Hover states on all interactive elements |
| NFR-USE-04 | Title attributes for full cell content |
| NFR-USE-05 | Loading spinners during AJAX |
| NFR-USE-06 | Meaningful empty states |
| NFR-USE-07 | Collapsible sidebar on mobile |

### 4.3 Reliability

| ID | Requirement |
|---|---|
| NFR-REL-01 | Handle missing dataset gracefully |
| NFR-REL-02 | Handle malformed CSV data |
| NFR-REL-03 | Handle NaT datetime values |
| NFR-REL-04 | Handle concurrent users |
| NFR-REL-05 | Django ORM transactions |

### 4.4 Security

| ID | Requirement |
|---|---|
| NFR-SEC-01 | CSRF protection on POST requests |
| NFR-SEC-02 | XSS prevention via template escaping |
| NFR-SEC-03 | Input validation on API parameters |
| NFR-SEC-04 | SQL injection prevention via ORM |

### 4.5 Maintainability

| ID | Requirement |
|---|---|
| NFR-MAINT-01 | Django MVT architecture |
| NFR-MAINT-02 | Business logic in service layers |
| NFR-MAINT-03 | API views return JSON, page views render templates |
| NFR-MAINT-04 | CSS variables for theming |
| NFR-MAINT-05 | Single App object in JavaScript |

### 4.6 Accessibility

| ID | Requirement |
|---|---|
| NFR-ACC-01 | Semantic HTML elements |
| NFR-ACC-02 | Alt text and aria labels |
| NFR-ACC-03 | Keyboard navigation |
| NFR-ACC-04 | WCAG AA color contrast |

---

## 5. Business Requirements

| ID | Requirement | Priority |
|---|---|---|
| BR-01 | Centralized space mission data platform | High |
| BR-02 | Data-driven decision making through analytics | High |
| BR-03 | All analytics generated dynamically | High |
| BR-04 | No hardcoded or fake analytics | High |
| BR-05 | Data export for offline analysis | Medium |
| BR-06 | Cost-effective open-source stack | Medium |
| BR-07 | Deployable on standard web servers | Medium |

---

## 6. User Requirements

| ID | Requirement | User Type |
|---|---|---|
| UR-01 | View mission statistics on dashboard | All |
| UR-02 | Browse all missions in paginated table | All |
| UR-03 | Search missions by any keyword | All |
| UR-04 | Filter missions by agency, country, status | Analyst |
| UR-05 | View interactive charts | All |
| UR-06 | Click chart segments for related missions | Analyst |
| UR-07 | Export data as CSV or Excel | Analyst |
| UR-08 | Save missions as bookmarks with links | All |
| UR-09 | Switch between dark and light themes | All |
| UR-10 | View column statistics and data quality | Analyst |

---

## 7. System Requirements

### 7.1 Hardware

| Component | Minimum | Recommended |
|---|---|---|
| Processor | Dual-core 1.5 GHz | Quad-core 2.0 GHz |
| RAM | 2 GB | 4 GB |
| Storage | 500 MB | 1 GB |

### 7.2 Software

| Component | Requirement |
|---|---|
| Python | 3.10+ |
| Django | 4.2+ |
| Pandas | 1.5+ |
| NumPy | 1.24+ |
| openpyxl | 3.0+ |
| SQLite | 3.x |
| Browser | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |

---

## 8. User Stories

### Dashboard
- US-DASH-01: See total missions on dashboard → KPI card shows accurate count
- US-DASH-02: See success/failure counts → KPI cards show correct values
- US-DASH-03: See missions-per-year chart → Line chart renders with data
- US-DASH-04: Click chart segment → Navigates to drill-down page

### Missions
- US-MISS-01: Browse all missions → Paginated table shows 25 per page
- US-MISS-02: Click mission row → Detail page shows all columns
- US-MISS-03: Bookmark mission → Saves with direct link

### Search
- US-SRCH-01: Search "SpaceX" → Table shows only SpaceX rows
- US-SRCH-02: Search updates as I type → Results update after 300ms

### Analytics
- US-ANAL-01: See mission status chart → Doughnut shows distribution
- US-ANAL-02: Click "Failure" → Drill-down shows 445 failure missions

### Reports
- US-RPTS-01: See dataset summary → 3D KPI cards display stats
- US-RPTS-02: Export CSV → Download triggers file save

---

## 9. Use Cases

### UC-01: View Dashboard
- Actor: User
- Flow: Navigate to / → System loads KPI cards → Renders charts → Shows insights
- Alternative: Empty dataset → Shows "No data loaded"

### UC-02: Search Missions
- Actor: User
- Flow: Type query → Debounce 300ms → AJAX request → Server filters → Table updates

### UC-03: Drill-Down from Chart
- Actor: User
- Flow: Click chart segment → Navigate to drilldown page → Load filtered missions → Paginate

### UC-04: Bookmark Mission
- Actor: User
- Flow: Click Bookmark → Capture name and link → POST to server → Show confirmation

### UC-05: Switch Theme
- Actor: User
- Flow: Click toggle → Switch data-bs-theme → Save to localStorage → Update all components

---

## 10. UML Diagrams

### 10.1 Class Diagram

```
+-------------------+       +---------------------+
|    Bookmark       |       |  FavoriteMission    |
+-------------------+       +---------------------+
| - id: Integer     |       | - id: Integer       |
| - mission_name:   |       | - mission_name:     |
|   CharField(500)  |       |   CharField(500)    |
| - mission_data:   |       | - mission_data:     |
|   JSONField       |       |   JSONField         |
|   {name, link, id}|       |   {name, link, id}  |
| - created_at:     |       | - created_at:       |
|   DateTimeField   |       |   DateTimeField     |
+-------------------+       +---------------------+

+-------------------+       +---------------------+
|   DataService     |       |   AnalyticsService  |
+-------------------+       +---------------------+
| + get_combined_   |       | + get_dashboard_    |
|   dataframe()     |       |   stats()           |
| + get_columns()   |       | + get_missions_     |
| + get_filter_     |       |   per_year()        |
|   options()       |       | + get_top_agencies()|
| + search_         |       | + get_agency_       |
|   dataframe()     |       |   comparison()      |
| + get_mission_    |       | + generate_         |
|   detail()        |       |   insights()        |
+-------------------+       | + get_statistics()  |
                            | + get_data_quality()|
                            +---------------------+
```

### 10.2 Activity Diagram: Drill-Down

```
[Start]
   v
[User clicks chart segment]
   v
[Chart.js onClick fires]
   v
[Get label from chartData.labels]
   v
[Navigate to /analytics/drilldown/<id>/?label=<label>]
   v
[Drill-down page loads]
   v
[Fetch filtered missions from API]
   v
[Server filters DataFrame by label]
   v
[Return paginated rows]
   v
[Render filtered table]
   v
[End]
```

### 10.3 Sequence Diagram

```
Browser              Django Server           Pandas/Cache
  |                       |                       |
  |  GET /                |                       |
  |---------------------->|  [Render sidebar]     |
  |<----------------------|                       |
  |                       |                       |
  |  GET /api/stats/      |                       |
  |---------------------->|  get_combined_        |
  |                       |  dataframe() -------->|
  |                       |<--- cached -----------|
  |<----------------------|                       |
  |                       |                       |
  |  [Render 3D KPIs]     |                       |
  |                       |                       |
  |  [User clicks chart]  |                       |
  |                       |                       |
  |  GET /analytics/      |                       |
  |  drilldown/<id>/?label|                       |
  |---------------------->|  [Filter DataFrame]   |
  |<----------------------|                       |
```

---

## 11. Data Dictionary

### 11.1 Dataset

| Column | Type | Example |
|---|---|---|
| Company Name | String | SpaceX, CASC, NASA |
| Location | String | LC-39A, Kennedy Space Center, Florida, USA |
| Datum | DateTime | Fri Aug 07, 2020 05:12 UTC |
| Detail | String | Falcon 9 Block 5 \| Starlink V1 L9 |
| Status Rocket | String | StatusActive, StatusRetired |
| Rocket | Float | 50.0, 29.75 |
| Status Mission | String | Success, Failure, Partial Failure |

### 11.2 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/stats/` | GET | Dashboard KPIs |
| `/api/insights/` | GET | Auto-generated insights |
| `/api/suggestions/?q=` | GET | Search suggestions |
| `/api/filters/` | GET | Filter options |
| `/missions/api/list/` | GET | Paginated missions |
| `/missions/api/detail/<id>/` | GET | Mission details |
| `/analytics/api/<chart_id>/` | GET | Chart data |
| `/analytics/api/<chart_id>/missions/` | GET | Drill-down missions |
| `/reports/api/summary/` | GET | Report summary |
| `/reports/api/statistics/` | GET | Statistics |
| `/reports/api/quality/` | GET | Data quality |
| `/reports/export/csv/` | GET | CSV export |
| `/reports/export/excel/` | GET | Excel export |
| `/bookmark/add/` | POST | Create bookmark |
| `/bookmark/remove/<id>/` | POST | Delete bookmark |

---

## 12. External Interface

### UI
- Bootstrap 5.3.2, Font Awesome 6.5.1, Chart.js 4.4.1
- Inter font (Google Fonts)
- Glassmorphic design with 3D effects
- Fixed sidebar + scrollable content

### Communication
- HTTP/HTTPS, JSON API responses, UTF-8 encoding

---

## 13. Glossary

| Term | Definition |
|---|---|
| CSV | Comma-Separated Values |
| DataFrame | Pandas two-dimensional data structure |
| Drill-Down | Click chart element to view filtered data |
| Glassmorphism | UI with blur effects and transparency |
| KPI | Key Performance Indicator |
| NaT | Not a Time (missing datetime) |
| MVT | Model-View-Template (Django pattern) |

---

*Document prepared on July 5, 2026*
*Space Missions Explorer - SCD Lab Project*
