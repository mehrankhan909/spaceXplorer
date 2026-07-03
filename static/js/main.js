(function () {
    'use strict';

    var App = {
        csrfToken: '',
        activeFilters: {},
        currentPage: 1,
        currentSort: '',
        currentSortDir: 'asc',
        pageSize: 25,
        chartInstances: {},

        init: function() {
            this.csrfToken = this.getCookie('csrftoken') || '';
            this.initTheme();
            this.initSidebar();
            this.initGlobalSearch();
            this.initKeyboardShortcuts();
            this.initPage();
        },

        initTheme: function() {
            var saved = localStorage.getItem('theme') || 'dark';
            document.documentElement.setAttribute('data-bs-theme', saved);
            var self = this;
            var toggle = document.getElementById('themeToggle');
            if (toggle) {
                toggle.innerHTML = saved === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
                toggle.addEventListener('click', function() {
                    var current = document.documentElement.getAttribute('data-bs-theme');
                    var next = current === 'dark' ? 'light' : 'dark';
                    document.documentElement.setAttribute('data-bs-theme', next);
                    localStorage.setItem('theme', next);
                    toggle.innerHTML = next === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
                    self.currentTheme = next;
                });
            }
            this.currentTheme = saved;
        },

        initSidebar: function() {
            var sidebar = document.getElementById('sidebar');
            var mobileBtn = document.getElementById('mobileMenuBtn');
            var overlay = document.getElementById('sidebarOverlay');
            if (mobileBtn && sidebar) {
                mobileBtn.addEventListener('click', function() {
                    sidebar.classList.toggle('mobile-open');
                    overlay.classList.toggle('active');
                });
            }
            if (overlay) {
                overlay.addEventListener('click', function() {
                    sidebar.classList.remove('mobile-open');
                    overlay.classList.remove('active');
                });
            }
            var path = window.location.pathname;
            document.querySelectorAll('.sidebar-link').forEach(function(link) {
                var href = link.getAttribute('href');
                if (href && (path === href || (href !== '/' && path.startsWith(href)))) {
                    link.classList.add('active');
                }
            });
        },

        initGlobalSearch: function() {
            var input = document.getElementById('globalSearch');
            var suggestionsEl = document.getElementById('searchSuggestions');
            if (!input || !suggestionsEl) return;
            var self = this;
            var debounceTimer;

            input.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                var q = input.value.trim();
                if (q.length < 2) { suggestionsEl.style.display = 'none'; return; }
                debounceTimer = setTimeout(function() {
                    fetch('/api/suggestions/?q=' + encodeURIComponent(q))
                        .then(function(r) { return r.json(); })
                        .then(function(data) {
                            var html = '';
                            if (data.suggestions && data.suggestions.length > 0) {
                                data.suggestions.forEach(function(s) {
                                    html += '<button type="button" class="list-group-item list-group-item-action d-flex align-items-center" data-value="' + self.escapeAttr(s) + '">' +
                                        '<i class="fas fa-search me-2 text-muted"></i>' + self.escapeHtml(s) + '</button>';
                                });
                            }
                            html += '<button type="button" class="list-group-item list-group-item-action d-flex align-items-center" data-search="' + self.escapeAttr(q) + '">' +
                                '<i class="fas fa-arrow-right me-2 text-muted"></i>Search for "' + self.escapeHtml(q) + '"</button>';
                            suggestionsEl.innerHTML = html;
                            suggestionsEl.style.display = 'block';
                        }).catch(function() {});
                }, 300);
            });

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    var q = input.value.trim();
                    if (q) window.location.href = '/missions/?q=' + encodeURIComponent(q);
                }
                if (e.key === 'Escape') { suggestionsEl.style.display = 'none'; input.blur(); }
            });

            suggestionsEl.addEventListener('click', function(e) {
                var item = e.target.closest('.list-group-item');
                if (!item) return;
                var val = item.dataset.value || item.dataset.search || '';
                window.location.href = '/missions/?q=' + encodeURIComponent(val);
            });

            document.addEventListener('click', function(e) {
                if (!input.contains(e.target) && !suggestionsEl.contains(e.target)) {
                    suggestionsEl.style.display = 'none';
                }
            });
        },

        initDataTable: function() {
            var searchInput = document.getElementById('tableSearch');
            if (!searchInput) return;
            var urlParams = new URLSearchParams(window.location.search);
            var initialQuery = urlParams.get('q') || '';
            if (initialQuery) searchInput.value = initialQuery;
            var debounceTimer;
            var self = this;
            searchInput.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(function() { self.currentPage = 1; self.loadData(); }, 300);
            });
            this.loadFilters();
            this.loadData();
        },

        loadFilters: function() {
            var self = this;
            fetch('/api/filters/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var grid = document.getElementById('filterGrid');
                    if (!grid || !data.options) return;
                    var html = '';
                    Object.keys(data.options).forEach(function(col) {
                        var options = data.options[col];
                        if (col === '_year_range') return;
                        if (Array.isArray(options) && options.length <= 100) {
                            html += '<div class="col-md-3 col-sm-6"><label class="form-label small text-muted">' + self.escapeHtml(col) + '</label>' +
                                '<select class="form-select form-select-sm bg-dark text-light border-secondary filter-select" data-column="' + self.escapeAttr(col) + '">' +
                                '<option value="">All ' + self.escapeHtml(col) + '</option>' +
                                options.map(function(v) { return '<option value="' + self.escapeAttr(v) + '">' + self.escapeHtml(v) + '</option>'; }).join('') +
                                '</select></div>';
                        }
                    });
                    grid.innerHTML = html || '<div class="col-12"><small class="text-muted">No filters available</small></div>';
                    self.bindFilters();
                }).catch(function() {
                    var grid = document.getElementById('filterGrid');
                    if (grid) grid.innerHTML = '<div class="col-12"><small class="text-muted">Failed to load filters</small></div>';
                });
        },

        bindFilters: function() {
            var self = this;
            document.querySelectorAll('.filter-select').forEach(function(el) {
                el.addEventListener('change', function() {
                    self.currentPage = 1;
                    self.collectFilters();
                    self.loadData();
                    self.renderActiveFilters();
                });
            });
            var resetBtn = document.getElementById('resetFilters');
            if (resetBtn) {
                resetBtn.addEventListener('click', function() {
                    self.activeFilters = {};
                    document.querySelectorAll('.filter-select').forEach(function(s) { s.value = ''; });
                    self.currentPage = 1;
                    self.loadData();
                    self.renderActiveFilters();
                });
            }
        },

        collectFilters: function() {
            this.activeFilters = {};
            var self = this;
            document.querySelectorAll('.filter-select').forEach(function(el) {
                if (el.value) self.activeFilters[el.dataset.column] = el.value;
            });
        },

        renderActiveFilters: function() {
            var container = document.getElementById('activeFilters');
            if (!container) return;
            var entries = Object.entries(this.activeFilters);
            if (entries.length === 0) { container.innerHTML = ''; return; }
            var self = this;
            container.innerHTML = entries.map(function(entry) {
                return '<span class="badge bg-primary me-1 mb-1" style="cursor:pointer;" data-key="' + self.escapeAttr(entry[0]) + '">' +
                    self.escapeHtml(entry[0]) + ': ' + self.escapeHtml(entry[1]) + ' <i class="fas fa-times ms-1"></i></span>';
            }).join('');
            container.querySelectorAll('.badge').forEach(function(badge) {
                badge.addEventListener('click', function() {
                    var key = badge.dataset.key;
                    delete self.activeFilters[key];
                    var select = document.querySelector('.filter-select[data-column="' + key + '"]');
                    if (select) select.value = '';
                    self.currentPage = 1;
                    self.loadData();
                    self.renderActiveFilters();
                });
            });
        },

        loadData: function() {
            var searchInput = document.getElementById('tableSearch');
            var q = searchInput ? searchInput.value.trim() : '';
            var params = new URLSearchParams();
            params.set('q', q);
            params.set('page', this.currentPage);
            params.set('page_size', this.pageSize);
            if (this.currentSort) { params.set('sort', this.currentSort); params.set('dir', this.currentSortDir); }
            var self = this;
            Object.entries(this.activeFilters).forEach(function(e) { params.set('filter_' + e[0], e[1]); });
            this.showTableLoading();
            fetch('/missions/api/list/?' + params.toString())
                .then(function(r) { return r.json(); })
                .then(function(data) { self.renderTable(data); self.renderPagination(data); self.updateResultCount(data); })
                .catch(function() { self.hideTableLoading(); });
        },

        showTableLoading: function() {
            var tbody = document.getElementById('tableBody');
            if (tbody) tbody.innerHTML = '<tr><td colspan="100" class="text-center py-5"><div class="loading-spinner"></div><p class="text-muted mt-2 small">Loading data...</p></td></tr>';
        },

        hideTableLoading: function() {},

        renderTable: function(data) {
            var tbody = document.getElementById('tableBody');
            if (!tbody) return;
            if (!data.rows || data.rows.length === 0) {
                tbody.innerHTML = '<tr><td colspan="100" class="text-center py-5"><i class="fas fa-inbox fa-2x text-muted mb-2"></i><p class="text-muted">No results found</p></td></tr>';
                return;
            }
            var columns = data.columns || [];
            var query = ((document.getElementById('tableSearch') || {}).value || '').trim().toLowerCase();
            var self = this;
            var thead = document.getElementById('tableHead');
            if (thead) {
                thead.innerHTML = '<th style="width:50px;">#</th>' +
                    columns.map(function(col) { return '<th style="cursor:pointer;" data-column="' + self.escapeAttr(col) + '">' + self.escapeHtml(col) + '</th>'; }).join('');
            }
            tbody.innerHTML = data.rows.map(function(row, i) {
                var rowIdx = (data.page - 1) * data.page_size + i;
                var cells = columns.map(function(col) {
                    var val = row[col] != null ? String(row[col]) : '\u2014';
                    if (val.length > 50) val = val.substring(0, 47) + '...';
                    if (query && val.toLowerCase().indexOf(query) !== -1) val = self.highlightText(val, query);
                    return '<td title="' + self.escapeAttr(row[col] != null ? String(row[col]) : '') + '">' + val + '</td>';
                }).join('');
                return '<tr style="cursor:pointer;" onclick="App.openDetail(' + rowIdx + ')"><td class="text-muted small">' + (rowIdx + 1) + '</td>' + cells + '</tr>';
            }).join('');
            this.initSorting();
        },

        renderPagination: function(data) {
            var wrapper = document.getElementById('pagination');
            if (!wrapper) return;
            var page = data.page, pages = data.pages, total = data.total;
            var self = this;
            var html = '<small class="text-muted">Showing ' + ((page - 1) * this.pageSize + 1) + '-' + Math.min(page * this.pageSize, total) + ' of ' + total.toLocaleString() + '</small>';
            html += '<nav><ul class="pagination pagination-sm mb-0">';
            html += '<li class="page-item' + (page <= 1 ? ' disabled' : '') + '"><a class="page-link" href="#" onclick="App.goToPage(' + (page - 1) + ');return false;">Prev</a></li>';
            var startPage = Math.max(1, page - 2), endPage = Math.min(pages, page + 2);
            if (startPage > 1) { html += '<li class="page-item"><a class="page-link" href="#" onclick="App.goToPage(1);return false;">1</a></li>'; if (startPage > 2) html += '<li class="page-item disabled"><span class="page-link">...</span></li>'; }
            for (var i = startPage; i <= endPage; i++) { html += '<li class="page-item' + (i === page ? ' active' : '') + '"><a class="page-link" href="#" onclick="App.goToPage(' + i + ');return false;">' + i + '</a></li>'; }
            if (endPage < pages) { if (endPage < pages - 1) html += '<li class="page-item disabled"><span class="page-link">...</span></li>'; html += '<li class="page-item"><a class="page-link" href="#" onclick="App.goToPage(' + pages + ');return false;">' + pages + '</a></li>'; }
            html += '<li class="page-item' + (page >= pages ? ' disabled' : '') + '"><a class="page-link" href="#" onclick="App.goToPage(' + (page + 1) + ');return false;">Next</a></li>';
            html += '</ul></nav>';
            wrapper.innerHTML = html;
        },

        updateResultCount: function(data) {
            var el = document.getElementById('resultCount');
            if (el) el.textContent = data.total.toLocaleString() + ' results';
        },

        goToPage: function(page) {
            this.currentPage = page;
            this.loadData();
        },

        initSorting: function() {
            var self = this;
            document.querySelectorAll('#tableHead th[data-column]').forEach(function(th) {
                th.addEventListener('click', function() {
                    var col = th.dataset.column;
                    if (self.currentSort === col) { self.currentSortDir = self.currentSortDir === 'asc' ? 'desc' : 'asc'; }
                    else { self.currentSort = col; self.currentSortDir = 'asc'; }
                    self.currentPage = 1;
                    self.loadData();
                });
            });
        },

        openDetail: function(id) { window.location.href = '/missions/detail/' + id + '/'; },

        initCharts: function() {
            var self = this;
            document.querySelectorAll('[data-chart-id]').forEach(function(el) {
                var chartId = el.dataset.chartId;
                if (!chartId) return;
                var canvas = document.createElement('canvas');
                el.innerHTML = '';
                el.appendChild(canvas);
                self.loadChart(chartId, el, canvas);
            });
        },

        loadChart: function(chartId, container, canvas) {
            var self = this;
            fetch('/analytics/api/' + chartId + '/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.data && data.data.labels && data.data.labels.length > 0) {
                        self.renderChart(canvas, chartId, data.data);
                    } else {
                        container.innerHTML = '<div class="text-center text-muted py-4"><i class="fas fa-chart-bar fa-2x mb-2"></i><p class="small">No data available</p></div>';
                    }
                }).catch(function() {
                    container.innerHTML = '<div class="text-center text-muted py-4"><p class="small">Failed to load chart</p></div>';
                });
        },

        renderChart: function(canvas, chartId, chartData) {
            var ctx = canvas.getContext('2d');
            var isDark = this.currentTheme === 'dark';
            var gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
            var textColor = isDark ? '#6c757d' : '#6c757d';
            var colors = ['#6c5ce7','#198754','#dc3545','#ffc107','#0dcaf0','#6f42c1','#fd7e14','#20c997','#d63384','#0d6efd','#e17055','#00b894','#636e72','#d63031','#0984e3'];
            var chartType = 'bar';
            if (chartId === 'mission_status' || chartId === 'rocket_status') chartType = 'doughnut';
            else if (chartId === 'missions_per_year' || chartId === 'success_rate_trend' || chartId === 'launch_frequency') chartType = 'line';

            var labelNames = {
                'missions_per_year': 'Missions', 'top_agencies': 'Missions', 'country_launches': 'Launches',
                'rocket_usage': 'Usage', 'monthly_launches': 'Launches', 'mission_status': 'Status',
                'rocket_status': 'Status', 'success_rate_trend': 'Success Rate %', 'launch_frequency': 'Launches'
            };
            var defaultLabel = labelNames[chartId] || 'Count';

            var self = this;
            var datasets;
            if (chartData.datasets) {
                datasets = chartData.datasets.map(function(ds, i) {
                    return { label: ds.label || ('Series ' + (i+1)), data: ds.data, backgroundColor: i === 0 ? 'rgba(108,92,231,0.7)' : 'rgba(255,107,107,0.7)', borderColor: i === 0 ? '#6c5ce7' : '#dc3545', borderWidth: 1, borderRadius: 4 };
                });
                chartType = 'bar';
            } else {
                var bg, bc, bw, fill, tension, pr;
                if (chartType === 'line') { bg = 'rgba(108,92,231,0.12)'; bc = '#6c5ce7'; bw = 2; fill = true; tension = 0.4; pr = 3; }
                else if (chartType === 'doughnut') { bg = colors.slice(0, chartData.data.length); bc = 'transparent'; bw = 0; fill = false; tension = 0; pr = 0; }
                else { bg = colors.slice(0, chartData.data.length); bc = 'transparent'; bw = 1; fill = false; tension = 0; pr = 0; }
                datasets = [{ label: defaultLabel, data: chartData.data, backgroundColor: bg, borderColor: bc, borderWidth: bw, fill: fill, tension: tension, pointRadius: pr, pointBackgroundColor: '#6c5ce7', borderRadius: chartType === 'bar' ? 4 : 0 }];
            }
            var isPie = chartType === 'pie' || chartType === 'doughnut';
            this.chartInstances[chartId] = new Chart(ctx, {
                type: chartType,
                data: { labels: chartData.labels, datasets: datasets },
                options: {
                    responsive: true, maintainAspectRatio: false, animation: { duration: 600 },
                    onClick: function(evt) {
                        var points = self.chartInstances[chartId].getElementsAtEventForMode(evt, 'nearest', { intersect: true }, false);
                        if (points.length > 0) {
                            var idx = points[0].index;
                            var label = chartData.labels[idx];
                            window.location.href = '/analytics/drilldown/' + chartId + '/?label=' + encodeURIComponent(String(label));
                        }
                    },
                    plugins: {
                        legend: { display: isPie || (chartData.datasets && chartData.datasets.length > 1), position: isPie ? 'right' : 'top', labels: { color: textColor, font: { size: 11 }, padding: 12, usePointStyle: true } },
                        tooltip: { backgroundColor: isDark ? '#1a1d21' : '#ffffff', titleColor: isDark ? '#e9ecef' : '#212529', bodyColor: textColor, borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)', borderWidth: 1, cornerRadius: 8, padding: 10 }
                    },
                    scales: isPie ? {} : {
                        x: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 10 }, maxRotation: 45 } },
                        y: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 10 } }, beginAtZero: true }
                    }
                }
            });
        },

        initDashboard: function() {
            this.loadDashboardStats();
            this.initCharts();
        },

        loadDashboardStats: function() {
            var grid = document.getElementById('kpiGrid');
            if (!grid) return;
            var self = this;
            fetch('/api/stats/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var kpis = [
                        { icon: 'fas fa-satellite', value: data.total_missions, label: 'Total Missions', color: 'primary', glow: '#6c5ce7' },
                        { icon: 'fas fa-check-circle', value: data.successful, label: 'Successful', color: 'success', glow: '#198754' },
                        { icon: 'fas fa-times-circle', value: data.failed, label: 'Failed', color: 'danger', glow: '#dc3545' },
                        { icon: 'fas fa-percentage', value: data.success_rate + '%', label: 'Success Rate', color: 'info', glow: '#0dcaf0' },
                        { icon: 'fas fa-building', value: data.agencies, label: 'Agencies', color: 'warning', glow: '#ffc107' },
                        { icon: 'fas fa-map-marker-alt', value: data.launch_sites, label: 'Launch Sites', color: 'purple', glow: '#6f42c1' },
                    ];
                    grid.innerHTML = kpis.map(function(kpi) {
                        return '<div class="col-lg-3 col-md-6"><div class="report-kpi-card report-kpi-' + kpi.color + '">' +
                            '<div class="report-kpi-icon"><i class="' + kpi.icon + '"></i></div>' +
                            '<div class="report-kpi-body"><div class="report-kpi-value" data-count="' + (typeof kpi.value === 'number' ? kpi.value : 0) + '" data-is-percent="' + (String(kpi.value).indexOf('%') !== -1 ? 'true' : 'false') + '">' + kpi.value + '</div>' +
                            '<div class="report-kpi-label">' + kpi.label + '</div></div>' +
                            '<div class="report-kpi-glow"></div></div></div>';
                    }).join('');
                    self.animateCounters();
                }).catch(function() {
                    grid.innerHTML = '<div class="col-12 text-center text-muted py-4">Failed to load stats</div>';
                });
        },

        animateCounters: function() {
            document.querySelectorAll('[data-count]').forEach(function(el) {
                var target = parseFloat(el.dataset.count);
                if (isNaN(target) || target === 0) return;
                var isPercent = el.dataset.isPercent === 'true';
                var startTime = performance.now();
                function animate(now) {
                    var progress = Math.min((now - startTime) / 800, 1);
                    var eased = 1 - Math.pow(1 - progress, 3);
                    el.textContent = isPercent ? (eased * target).toFixed(1) + '%' : Math.round(eased * target).toLocaleString();
                    if (progress < 1) requestAnimationFrame(animate);
                }
                requestAnimationFrame(animate);
            });
        },

        loadInsights: function() {
            var container = document.getElementById('insightsContainer');
            if (!container) return;
            var self = this;
            fetch('/api/insights/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.insights && data.insights.length > 0) {
                        var colors = ['primary', 'success', 'info', 'warning', 'danger'];
                        container.innerHTML = data.insights.map(function(insight, i) {
                            var c = colors[i % colors.length];
                            return '<div class="col-md-6"><div class="insight-item border-' + c + '">' +
                                '<div class="insight-number">' + (i + 1) + '</div>' +
                                '<div class="insight-text">' + self.escapeHtml(insight) + '</div></div></div>';
                        }).join('');
                    } else {
                        container.innerHTML = '<div class="col-12 text-muted small">No insights available</div>';
                    }
                }).catch(function() {
                    container.innerHTML = '<div class="col-12 text-muted small">Failed to load insights</div>';
                });
        },

        initDetail: function() {
            var container = document.getElementById('missionDetail');
            if (!container) return;
            var missionId = container.dataset.missionId;
            if (!missionId) return;
            var self = this;
            fetch('/missions/api/detail/' + missionId + '/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.mission) self.renderDetail(data.mission, data.mission_id);
                    else container.innerHTML = '<div class="card"><div class="card-body text-center py-5"><i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i><p>Mission not found</p></div></div>';
                }).catch(function() {
                    container.innerHTML = '<div class="card"><div class="card-body text-center py-5 text-muted">Failed to load mission details</div></div>';
                });
        },

        renderDetail: function(mission, id) {
            var container = document.getElementById('missionDetail');
            if (!container) return;
            var self = this;
            var subtitle = document.getElementById('detailSubtitle');
            if (subtitle) {
                var firstKey = Object.keys(mission)[0];
                if (firstKey) subtitle.textContent = mission[firstKey];
            }
            var fieldsHtml = Object.entries(mission).map(function(entry) {
                return '<div class="col-md-6 col-lg-4 mb-3"><div class="detail-field"><div class="detail-field-label">' + self.escapeHtml(entry[0]) + '</div><div class="detail-field-value">' + self.escapeHtml(String(entry[1])) + '</div></div></div>';
            }).join('');
            container.innerHTML = '<div class="row g-3"><div class="col-lg-8"><div class="report-section-card">' +
                '<div class="report-section-header"><i class="fas fa-satellite me-2 text-primary"></i>Mission Information</div>' +
                '<div class="report-section-body"><div class="row">' + fieldsHtml + '</div></div></div></div>' +
                '<div class="col-lg-4"><div class="report-section-card mb-3">' +
                '<div class="report-section-header"><i class="fas fa-cog me-2"></i>Actions</div>' +
                '<div class="report-section-body d-flex flex-column gap-2">' +
                '<button class="btn glass-btn" onclick="App.bookmarkMission(' + id + ')" id="bookmarkBtn"><i class="fas fa-bookmark me-1"></i>Bookmark</button>' +
                '<button class="btn glass-btn" onclick="window.print()"><i class="fas fa-print me-1"></i>Print</button>' +
                '<a href="/reports/export/csv/" class="btn glass-btn" style="text-decoration:none;"><i class="fas fa-download me-1"></i>Export CSV</a>' +
                '<a href="/missions/" class="btn glass-btn" style="text-decoration:none;"><i class="fas fa-arrow-left me-1"></i>Back to List</a>' +
                '</div></div></div></div>';
        },

        bookmarkMission: function(id) {
            var self = this;
            var missionName = '';
            var missionLink = '/missions/detail/' + id + '/';
            var detailEl = document.getElementById('missionDetail');
            if (detailEl) {
                var fields = detailEl.querySelectorAll('.detail-field');
                if (fields.length > 0) {
                    var firstVal = fields[0].querySelector('.detail-field-value');
                    if (firstVal) missionName = firstVal.textContent.trim();
                }
            }
            if (!missionName) missionName = 'Mission #' + id;
            var payload = { name: missionName, link: missionLink, id: id };
            fetch('/bookmark/add/', {
                method: 'POST',
                headers: { 'X-CSRFToken': this.csrfToken, 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'mission_name=' + encodeURIComponent(missionName) + '&mission_data=' + encodeURIComponent(JSON.stringify(payload))
            }).then(function(r) { return r.json(); }).then(function(data) {
                if (data.status === 'ok') {
                    var btn = document.getElementById('bookmarkBtn');
                    if (btn) { btn.innerHTML = '<i class="fas fa-check me-1"></i>Bookmarked'; btn.className = 'btn btn-success'; }
                    self.showToast('Mission bookmarked', 'success');
                }
            });
        },

        initReports: function() { this.loadReportSummary(); },

        loadReportSummary: function() {
            var container = document.getElementById('reportSummary');
            if (!container) return;
            var self = this;
            fetch('/reports/api/summary/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var html = '';
                    html += '<div class="row g-3 mb-4">';
                    html += '<div class="col-md-4"><div class="report-kpi-card report-kpi-primary">' +
                        '<div class="report-kpi-icon"><i class="fas fa-database"></i></div>' +
                        '<div class="report-kpi-body"><div class="report-kpi-value">' + data.total_rows.toLocaleString() + '</div>' +
                        '<div class="report-kpi-label">Total Records</div></div>' +
                        '<div class="report-kpi-glow"></div></div></div>';
                    html += '<div class="col-md-4"><div class="report-kpi-card report-kpi-info">' +
                        '<div class="report-kpi-icon"><i class="fas fa-columns"></i></div>' +
                        '<div class="report-kpi-body"><div class="report-kpi-value">' + data.columns.length + '</div>' +
                        '<div class="report-kpi-label">Data Columns</div></div>' +
                        '<div class="report-kpi-glow"></div></div></div>';
                    html += '<div class="col-md-4"><div class="report-kpi-card report-kpi-success">' +
                        '<div class="report-kpi-icon"><i class="fas fa-clock"></i></div>' +
                        '<div class="report-kpi-body"><div class="report-kpi-value report-kpi-small">' + data.generated_at + '</div>' +
                        '<div class="report-kpi-label">Generated At</div></div>' +
                        '<div class="report-kpi-glow"></div></div></div>';
                    html += '</div>';

                    html += '<div class="row g-3 mb-4">';
                    html += '<div class="col-12"><div class="report-section-card">' +
                        '<div class="report-section-header"><i class="fas fa-columns me-2 text-primary"></i>Available Columns</div>' +
                        '<div class="report-section-body"><div class="d-flex flex-wrap gap-2">';
                    data.columns.forEach(function(col) {
                        html += '<span class="report-column-badge">' + self.escapeHtml(col) + '</span>';
                    });
                    html += '</div></div></div></div></div>';

                    if (data.insights.length > 0) {
                        html += '<div class="row g-3">';
                        html += '<div class="col-12"><div class="report-section-card">' +
                            '<div class="report-section-header"><i class="fas fa-lightbulb me-2 text-warning"></i>Key Insights</div>' +
                            '<div class="report-section-body"><div class="row g-2">';
                        data.insights.forEach(function(insight, i) {
                            var colors = ['primary', 'success', 'info', 'warning', 'danger'];
                            var c = colors[i % colors.length];
                            html += '<div class="col-md-6"><div class="insight-item border-' + c + '">' +
                                '<div class="insight-number">' + (i + 1) + '</div>' +
                                '<div class="insight-text">' + self.escapeHtml(insight) + '</div></div></div>';
                        });
                        html += '</div></div></div></div></div>';
                    }
                    container.innerHTML = html;
                });
        },

        loadStatistics: function() {
            var container = document.getElementById('statisticsContainer');
            if (!container) return;
            var self = this;
            fetch('/reports/api/statistics/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (!data.stats || Object.keys(data.stats).length === 0) { container.innerHTML = '<div class="text-center text-muted py-5"><i class="fas fa-chart-bar fa-3x mb-3 d-block"></i><p>No statistics available</p></div>'; return; }
                    var html = '';
                    if (data.stats.meta) {
                        var m = data.stats.meta;
                        html += '<div class="row g-3 mb-4">';
                        var metaCards = [
                            { val: m.total_rows.toLocaleString(), label: 'Total Rows', icon: 'fas fa-table', color: 'primary' },
                            { val: m.total_columns, label: 'Columns', icon: 'fas fa-columns', color: 'info' },
                            { val: m.missing_values.toLocaleString(), label: 'Missing Values', icon: 'fas fa-exclamation-triangle', color: 'warning' },
                            { val: m.duplicate_rows, label: 'Duplicates', icon: 'fas fa-copy', color: 'danger' },
                        ];
                        metaCards.forEach(function(card) {
                            html += '<div class="col-lg-3 col-md-6"><div class="stat-3d-card stat-3d-' + card.color + '">' +
                                '<div class="stat-3d-icon"><i class="' + card.icon + '"></i></div>' +
                                '<div class="stat-3d-value">' + card.val + '</div>' +
                                '<div class="stat-3d-label">' + card.label + '</div>' +
                                '<div class="stat-3d-shine"></div></div></div>';
                        });
                        html += '</div>';
                    }

                    var colNames = Object.keys(data.stats).filter(function(k) { return k !== 'meta'; });
                    html += '<div class="row g-3">';
                    colNames.forEach(function(colName, idx) {
                        var colStats = data.stats[colName];
                        var entries = Object.entries(colStats);
                        var isNumeric = entries.some(function(e) { return e[0] === 'mean'; });
                        var accentColor = isNumeric ? '#6c5ce7' : '#00cec9';

                        html += '<div class="col-lg-4 col-md-6">' +
                            '<div class="stat-col-card">' +
                            '<div class="stat-col-header" style="border-left:3px solid ' + accentColor + ';">' +
                            '<span class="stat-col-name">' + self.escapeHtml(colName) + '</span>' +
                            '<span class="stat-col-type">' + (isNumeric ? 'numeric' : 'categorical') + '</span>' +
                            '</div>' +
                            '<div class="stat-col-body">';
                        entries.forEach(function(e) {
                            var val = e[1] != null ? e[1] : '-';
                            if (typeof val === 'number') val = val.toLocaleString();
                            html += '<div class="stat-col-row">' +
                                '<span class="stat-col-key">' + self.escapeHtml(e[0]) + '</span>' +
                                '<span class="stat-col-val">' + val + '</span>' +
                                '</div>';
                        });
                        html += '</div></div></div>';
                    });
                    html += '</div>';
                    container.innerHTML = html;
                });
        },

        loadDataQuality: function() {
            var container = document.getElementById('qualityContainer');
            if (!container) return;
            var self = this;
            fetch('/reports/api/quality/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (!data.quality || !data.quality.columns) { container.innerHTML = '<div class="text-center text-muted py-5"><p>No quality data available</p></div>'; return; }
                    var q = data.quality;
                    var totalNulls = 0;
                    var totalUnique = 0;
                    Object.values(q.columns).forEach(function(c) { totalNulls += c.null_count; totalUnique += c.unique_count; });
                    var overallScore = Math.round(100 - (totalNulls / (q.total_rows * q.total_columns) * 100));

                    var html = '<div class="row g-3 mb-4">';
                    var qCards = [
                        { val: q.total_rows.toLocaleString(), label: 'Total Rows', icon: 'fas fa-table', color: 'primary', bg: 'rgba(108,92,231,0.15)' },
                        { val: q.total_columns, label: 'Columns', icon: 'fas fa-columns', color: 'info', bg: 'rgba(13,202,240,0.15)' },
                        { val: overallScore + '%', label: 'Quality Score', icon: 'fas fa-shield-alt', color: overallScore > 80 ? 'success' : (overallScore > 50 ? 'warning' : 'danger'), bg: overallScore > 80 ? 'rgba(25,135,84,0.15)' : 'rgba(255,193,7,0.15)' },
                    ];
                    qCards.forEach(function(card) {
                        html += '<div class="col-md-4"><div class="quality-hero-card">' +
                            '<div class="quality-hero-icon" style="background:' + card.bg + ';color:var(--accent);"><i class="' + card.icon + '"></i></div>' +
                            '<div class="quality-hero-value">' + card.val + '</div>' +
                            '<div class="quality-hero-label">' + card.label + '</div>' +
                            '<div class="quality-hero-ring" style="border-color:' + card.bg + ';"></div></div></div>';
                    });
                    html += '</div>';

                    html += '<div class="quality-table-wrapper"><div class="quality-table-header">' +
                        '<h6 class="mb-0"><i class="fas fa-list-check me-2 text-primary"></i>Column Quality Details</h6></div>';
                    html += '<div class="table-responsive"><table class="table align-middle mb-0"><thead><tr>' +
                        '<th>Column</th><th>Type</th><th>Nulls</th><th>Null %</th><th>Unique</th><th>Quality</th>' +
                        '</tr></thead><tbody>';
                    Object.entries(q.columns).forEach(function(entry) {
                        var name = entry[0], info = entry[1];
                        var pct = info.null_percent;
                        var quality = pct > 50 ? 'poor' : (pct > 10 ? 'fair' : 'good');
                        var color = quality === 'good' ? '#198754' : (quality === 'fair' ? '#ffc107' : '#dc3545');
                        var label = quality === 'good' ? 'Good' : (quality === 'fair' ? 'Fair' : 'Poor');
                        html += '<tr>' +
                            '<td><div class="d-flex align-items-center gap-2">' +
                            '<div class="quality-dot" style="background:' + color + ';"></div>' +
                            '<strong>' + self.escapeHtml(name) + '</strong></div></td>' +
                            '<td><span class="quality-type-badge">' + info.dtype + '</span></td>' +
                            '<td class="text-center">' + info.null_count.toLocaleString() + '</td>' +
                            '<td><div class="quality-pct-bar"><div class="quality-pct-fill" style="width:' + Math.min(pct, 100) + '%;background:' + color + ';"></div></div>' +
                            '<small class="text-muted">' + pct + '%</small></td>' +
                            '<td class="text-center">' + info.unique_count.toLocaleString() + '</td>' +
                            '<td><span class="quality-badge quality-' + quality + '">' + label + '</span></td>' +
                            '</tr>';
                    });
                    html += '</tbody></table></div></div>';
                    container.innerHTML = html;
                });
        },

        getCookie: function(name) {
            var v = '; ' + document.cookie;
            var p = v.split('; ' + name + '=');
            return p.length === 2 ? p.pop().split(';').shift() : '';
        },

        escapeHtml: function(str) {
            if (!str) return '';
            var d = document.createElement('div'); d.textContent = str; return d.innerHTML;
        },

        escapeAttr: function(str) {
            if (!str) return '';
            return str.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        },

        highlightText: function(text, query) {
            if (!query) return this.escapeHtml(text);
            var esc = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            return this.escapeHtml(text).replace(new RegExp('(' + esc + ')', 'gi'), '<span class="cell-highlight">$1</span>');
        },

        showToast: function(message, type) {
            type = type || 'info';
            var container = document.querySelector('.toast-container');
            if (!container) { container = document.createElement('div'); container.className = 'toast-container position-fixed top-0 end-0 p-3'; container.style.zIndex = '1090'; document.body.appendChild(container); }
            var toast = document.createElement('div');
            toast.className = 'toast show';
            var iconMap = { success: 'check-circle text-success', danger: 'times-circle text-danger', warning: 'exclamation-triangle text-warning', info: 'info-circle text-info' };
            toast.innerHTML = '<div class="toast-body d-flex align-items-center"><i class="fas fa-' + (iconMap[type] || 'info-circle text-info') + ' me-2"></i>' + message + '</div>';
            container.appendChild(toast);
            setTimeout(function() { toast.classList.remove('show'); setTimeout(function() { toast.remove(); }, 300); }, 3000);
        },

        initKeyboardShortcuts: function() {
            document.addEventListener('keydown', function(e) {
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); var s = document.getElementById('globalSearch'); if (s) s.focus(); }
            });
        },

        initPage: function() {
            var page = document.body.dataset.page;
            switch (page) {
                case 'dashboard': this.initDashboard(); this.loadInsights(); break;
                case 'missions': this.initDataTable(); break;
                case 'detail': this.initDetail(); break;
                case 'analytics': case 'charts': this.initCharts(); break;
                case 'reports': this.initReports(); break;
                case 'statistics': this.loadStatistics(); break;
                case 'data-quality': this.loadDataQuality(); break;
            }
        }
    };

    window.App = App;
    document.addEventListener('DOMContentLoaded', function() { App.init(); });
})();
