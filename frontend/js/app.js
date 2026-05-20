
document.addEventListener("DOMContentLoaded", async () => {
    // State management variables
    let allMovies = [];
    let chartsInitialized = false;
    let currentRecommendations = [];
    
    // Core Elements
    const sidebarMenuItems = document.querySelectorAll(".menu-item");
    const viewSections = document.querySelectorAll(".dashboard-view-section");
    const viewTitle = document.getElementById("view-title");
    const viewSubtitle = document.getElementById("view-subtitle");
    
    const searchInput = document.getElementById("dashboard-search-input");
    const suggestionsList = document.getElementById("dashboard-autocomplete-list");
    const searchBtn = document.getElementById("dashboard-search-btn");
    
    const recsGrid = document.getElementById("recommendations-grid");
    const recsLoader = document.getElementById("recommendations-loader");
    const recsEmpty = document.getElementById("recommendations-empty");
    const searchMetaHeader = document.getElementById("search-meta-header");
    const searchQueryHighlight = document.getElementById("search-query-highlight");
    
    // Modal Elements
    const modal = document.getElementById("movie-detail-modal");
    const modalCloseBtn = document.getElementById("modal-close-btn");
    const modalPoster = document.getElementById("modal-poster");
    const modalTitle = document.getElementById("modal-title");
    const modalRating = document.getElementById("modal-rating");
    const modalYear = document.getElementById("modal-year");
    const modalSimilarity = document.getElementById("modal-similarity");
    const modalTagline = document.getElementById("modal-tagline");
    const modalOverview = document.getElementById("modal-overview");
    const modalDirector = document.getElementById("modal-director");
    const modalGenres = document.getElementById("modal-genres");
    const modalCast = document.getElementById("modal-cast");
    const modalPopularity = document.getElementById("modal-popularity");
    const modalVotes = document.getElementById("modal-votes");
    const modalViewSimilarBtn = document.getElementById("modal-view-similar-btn");

    // SIDEBAR TAB 
    
    const viewMeta = {
        "home-view": {
            title: "Welcome back!",
            subtitle: "Explore your cinema minds."
        },
        "recommend-view": {
            title: "AI Recommendation Dashboard",
            subtitle: "Personalized cinematic weights computed by our similarity engine."
        },
        "analytics-view": {
            title: "Database Analytics Panel",
            subtitle: "Interactive data dimensions across 4,800+ titles in the TMDB database."
        }
    };

    function switchView(targetViewId) {
        // Toggle menu items active state
        sidebarMenuItems.forEach(item => {
            if (item.getAttribute("data-target") === targetViewId) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        // Toggle sections visibility
        viewSections.forEach(section => {
            if (section.id === targetViewId) {
                section.classList.add("active");
            } else {
                section.classList.remove("active");
            }
        });

        // Update headers
        const meta = viewMeta[targetViewId];
        if (meta) {
            viewTitle.textContent = meta.title;
            viewSubtitle.textContent = meta.subtitle;
        }

        // Initialize charts if entering analytics view
        if (targetViewId === "analytics-view" && !chartsInitialized) {
            loadAndRenderAnalytics();
        }
    }

    sidebarMenuItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const target = item.getAttribute("data-target");
            switchView(target);
        });
    });

    // Make switchView globally accessible for landing page triggers
    window.triggerQuickSearch = (movieName) => {
        searchInput.value = movieName;
        executeSearch(movieName);
    };

    window.focusSearch = () => {
        searchInput.focus();
    };

    // SEARCH AUTOCOMPLETE dropdown 

    // Fetch movies list on launch
    try {
        allMovies = await MovieMindAPI.getMoviesList();
        console.log(`[Dashboard] Autocomplete list populated with ${allMovies.length} movies.`);
    } catch (err) {
        console.error("Dashboard failed to preload autocomplete list:", err);
    }

    searchInput.addEventListener("input", () => {
        const val = searchInput.value.trim().toLowerCase();
        suggestionsList.innerHTML = "";
        
        if (!val) {
            suggestionsList.style.display = "none";
            return;
        }
        
        const matches = allMovies
            .filter(m => m.toLowerCase().includes(val))
            .slice(0, 8);
            
        if (matches.length > 0) {
            matches.forEach(match => {
                const div = document.createElement("div");
                div.className = "suggestion-item";
                div.textContent = match;
                div.addEventListener("click", () => {
                    searchInput.value = match;
                    suggestionsList.style.display = "none";
                    executeSearch(match);
                });
                suggestionsList.appendChild(div);
            });
            suggestionsList.style.display = "block";
        } else {
            suggestionsList.style.display = "none";
        }
    });

    // Close suggestions on outside click
    document.addEventListener("click", (e) => {
        if (e.target !== searchInput && e.target !== suggestionsList) {
            suggestionsList.style.display = "none";
        }
    });

    // Trigger searches on button clicks or Enter key press
    const handleSearchSubmit = () => {
        const query = searchInput.value.trim();
        if (query) {
            executeSearch(query);
        }
    };

    searchBtn.addEventListener("click", handleSearchSubmit);
    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            handleSearchSubmit();
        }
    });

    // Check if landing page passed a search query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get("search");
    if (searchQuery) {
        searchInput.value = searchQuery;
        executeSearch(searchQuery);
    }

    // SEARCH EXECUTION & RECOMMENDATION CARD

    async function executeSearch(movieTitle) {
        // Toggle view
        switchView("recommend-view");
        
        // Setup loading state
        searchMetaHeader.style.display = "none";
        recsEmpty.style.display = "none";
        recsGrid.style.display = "none";
        recsLoader.style.display = "flex";
        
        try {
            console.log(`[Dashboard] Sending API call for movie recommendations: ${movieTitle}`);
            const data = await MovieMindAPI.getRecommendations(movieTitle);
            currentRecommendations = data;
            
            recsLoader.style.display = "none";
            
            if (!data || data.length === 0) {
                // Return empty/no matches state
                recsEmpty.style.display = "block";
                recsEmpty.querySelector("h3").textContent = "No Movie Matches Found";
                recsEmpty.querySelector("p").textContent = `We couldn't find matches for "${movieTitle}". Please double check your spelling or search another movie!`;
                return;
            }
            
            // Set headers metadata
            searchQueryHighlight.textContent = `"${movieTitle}"`;
            searchMetaHeader.style.display = "block";
            
            // Render Cards Grid
            renderMovieCards(data);
            recsGrid.style.display = "grid";
            
        } catch (error) {
            console.error("Failed to render recommendations:", error);
            recsLoader.style.display = "none";
            recsEmpty.style.display = "block";
            recsEmpty.querySelector("h3").textContent = "API Communication Error";
            recsEmpty.querySelector("p").textContent = "There was a problem contacting the recommendation server. Please check that the backend is running.";
        }
    }

    function renderMovieCards(movies) {
        recsGrid.innerHTML = "";
        
        movies.forEach((movie, index) => {
            const card = document.createElement("div");
            card.className = "movie-card";
            
            // Poster handling (live TMDB image or beautiful CSS gradient fallback)
            let posterHtml = "";
            if (movie.poster_url && !movie.poster_url.startsWith("placeholder-")) {
                posterHtml = `<img src="${movie.poster_url}" alt="${movie.title}" class="card-poster" loading="lazy">`;
            } else {
                // Generate a cinematic linear gradient
                const gradients = [
                    "linear-gradient(135deg, #1c1917 0%, #44403c 100%)",
                    "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
                    "linear-gradient(135deg, #180828 0%, #3b0764 100%)",
                    "linear-gradient(135deg, #022c22 0%, #064e3b 100%)",
                    "linear-gradient(135deg, #1c0c0c 0%, #450a0a 100%)"
                ];
                const selectedGrad = gradients[index % gradients.length];
                posterHtml = `
                    <div class="poster-fallback" style="background: ${selectedGrad}">
                        <i class="fa-solid fa-clapperboard"></i>
                        <div class="poster-fallback-title">${movie.title}</div>
                    </div>
                `;
            }
            
            // Star rating mapping
            const stars = parseFloat(movie.vote_average);
            
            card.innerHTML = `
                <div class="card-poster-wrapper">
                    <span class="card-match-badge"><i class="fa-solid fa-heart-pulse"></i> ${movie.similarity_score}% Match</span>
                    ${posterHtml}
                </div>
                <div class="card-content">
                    <h4 class="card-title" title="${movie.title}">${movie.title}</h4>
                    <p class="card-genres" title="${movie.genres}">${movie.genres || "General Cinema"}</p>
                    <div class="card-meta">
                        <span class="card-rating">
                            <i class="fa-solid fa-star"></i> ${stars ? stars.toFixed(1) : "0.0"}
                        </span>
                        <span class="card-year">${movie.release_year || "N/A"}</span>
                    </div>
                </div>
            `;
            
            // Open detail modal on click
            card.addEventListener("click", () => {
                openDetailModal(movie);
            });
            
            recsGrid.appendChild(card);
        });
    }

    // =MOVIE DYNAMIC DETAIL MODAL 

    function openDetailModal(movie) {
        console.log(`[Modal] Opening detailed sheet for: ${movie.title}`);
        
        // 1. Setup poster details
        modalPoster.innerHTML = "";
        if (movie.poster_url && !movie.poster_url.startsWith("placeholder-")) {
            modalPoster.innerHTML = `<img src="${movie.poster_url}" alt="${movie.title}">`;
        } else {
            modalPoster.innerHTML = `
                <div class="poster-fallback" style="width:100%; height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center; background:linear-gradient(135deg, #18181b 0%, #27272a 100%);">
                    <i class="fa-solid fa-clapperboard" style="font-size: 4rem; color: var(--primary); margin-bottom:15px;"></i>
                    <div class="poster-fallback-title" style="font-size:1.3rem; font-family:'Outfit';">${movie.title}</div>
                </div>
            `;
        }

        // 2. Set text nodes
        modalTitle.textContent = movie.title;
        modalRating.innerHTML = `<i class="fa-solid fa-star"></i> ${movie.vote_average ? movie.vote_average.toFixed(1) : "0.0"}`;
        modalYear.textContent = movie.release_year || "N/A";
        modalSimilarity.textContent = `${movie.similarity_score}% Match`;
        modalTagline.textContent = movie.tagline ? `"${movie.tagline}"` : "Cinematic Masterpiece";
        modalOverview.textContent = movie.overview || "No overview available for this title.";
        modalDirector.textContent = movie.director || "Unknown Director";
        modalGenres.textContent = movie.genres || "Cinematic Genre";
        modalCast.textContent = movie.cast || "Cast details not available";
        modalPopularity.textContent = movie.popularity ? movie.popularity.toFixed(2) : "0.00";
        modalVotes.textContent = movie.vote_count ? `${movie.vote_count.toLocaleString()} votes` : "0 votes";

        // Close button overlay
        modal.classList.add("open");
        
        // Setup "View Similar" nested search within modal
        const newBtn = modalViewSimilarBtn.cloneNode(true);
        modalViewSimilarBtn.parentNode.replaceChild(newBtn, modalViewSimilarBtn);
        
        newBtn.addEventListener("click", () => {
            modal.classList.remove("open");
            searchInput.value = movie.title;
            executeSearch(movie.title);
        });
    }

    const closeModal = () => {
        modal.classList.remove("open");
    };

    modalCloseBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // CHART ANALYTICS 

    // Global Chart.js dark-mode defaults
    Chart.defaults.color = "#a1a1aa"; // var(--text-muted)
    Chart.defaults.borderColor = "rgba(255, 255, 255, 0.05)";
    Chart.defaults.font.family = "'Inter', sans-serif";

    async function loadAndRenderAnalytics() {
        const analyticsLoader = document.getElementById("analytics-loader");
        const analyticsContent = document.getElementById("analytics-content");
        
        analyticsLoader.style.display = "flex";
        analyticsContent.style.display = "none";
        
        try {
            console.log("[Analytics] Requesting aggregated analytics payload...");
            const data = await MovieMindAPI.getAnalyticsData();
            
            analyticsLoader.style.display = "none";
            analyticsContent.style.display = "block";
            
            // Render 4 beautiful, styled charts
            renderGenreChart(data.genres);
            renderRatingChart(data.top_rated);
            renderTrendsChart(data.trends);
            renderScatterChart(data.scatter);
            
            chartsInitialized = true;
            console.log("[Analytics] 4 interactive dark-mode charts successfully mounted.");
            
        } catch (err) {
            console.error("Failed to load and build analytics panel charts:", err);
            analyticsLoader.querySelector("p").textContent = "API Error: Verify Flask server connection to pull charts data.";
        }
    }

    function renderGenreChart(genreData) {
        const ctx = document.getElementById("genreChart").getContext("2d");
        
        // Gradient fill for bars
        const grad = ctx.createLinearGradient(0, 0, 400, 0);
        grad.addColorStop(0, "rgba(229, 9, 20, 0.85)"); // Red
        grad.addColorStop(1, "rgba(245, 158, 11, 0.85)"); // Amber
        
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: genreData.labels,
                datasets: [{
                    label: "Number of Movies",
                    data: genreData.values,
                    backgroundColor: grad,
                    borderColor: "var(--primary)",
                    borderWidth: 1,
                    borderRadius: 6,
                    barThickness: 16
                }]
            },
            options: {
                indexAxis: 'y', // Horizontal bars
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { drawOnChartArea: true } },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    function renderRatingChart(movies) {
        const ctx = document.getElementById("ratingChart").getContext("2d");
        
        const labels = movies.map(m => m.title);
        const ratings = movies.map(m => m.rating);
        
        const grad = ctx.createLinearGradient(0, 0, 0, 300);
        grad.addColorStop(0, "rgba(245, 158, 11, 0.85)"); // Amber
        grad.addColorStop(1, "rgba(229, 9, 20, 0.25)"); // Red
        
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Rating (Out of 10)",
                    data: ratings,
                    backgroundColor: grad,
                    borderColor: "var(--accent)",
                    borderWidth: 1,
                    borderRadius: 6,
                    barThickness: 22
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: {
                            callback: function(val, index) {
                                // Truncate long movie titles on X labels
                                const label = labels[index];
                                return label && label.length > 10 ? label.slice(0, 10) + "..." : label;
                            }
                        },
                        grid: { display: false }
                    },
                    y: {
                        min: 6,
                        max: 9,
                        grid: { drawOnChartArea: true }
                    }
                }
            }
        });
    }

    function renderTrendsChart(trends) {
        const ctx = document.getElementById("trendsChart").getContext("2d");
        
        const grad = ctx.createLinearGradient(0, 0, 0, 300);
        grad.addColorStop(0, "rgba(74, 222, 128, 0.3)"); // Glowing Green
        grad.addColorStop(1, "rgba(9, 9, 11, 0)");
        
        new Chart(ctx, {
            type: "line",
            data: {
                labels: trends.years,
                datasets: [{
                    label: "Movies Released",
                    data: trends.counts,
                    borderColor: "#4ade80",
                    borderWidth: 2,
                    fill: true,
                    backgroundColor: grad,
                    tension: 0.4, // Smooth curve spline
                    pointBackgroundColor: "#4ade80",
                    pointRadius: 3,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { drawOnChartArea: true } }
                }
            }
        });
    }

    function renderScatterChart(scatterData) {
        const ctx = document.getElementById("scatterChart").getContext("2d");
        
        new Chart(ctx, {
            type: "scatter",
            data: {
                datasets: [{
                    label: "Movies",
                    data: scatterData,
                    backgroundColor: "rgba(96, 165, 250, 0.6)", // custom glowing blue
                    borderColor: "#60a5fa",
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const pt = context.raw;
                                return `🎬 ${pt.title} | Rating: ${pt.x} | Popularity: ${pt.y.toFixed(1)}`;
                            }
                        }
                    },
                    legend: { display: false }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Vote Average (Rating)',
                            font: { weight: 'bold' }
                        },
                        grid: { drawOnChartArea: true }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Popularity Score',
                            font: { weight: 'bold' }
                        },
                        grid: { drawOnChartArea: true }
                    }
                }
            }
        });
    }
});
