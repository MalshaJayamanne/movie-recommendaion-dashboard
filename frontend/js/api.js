
const MovieMindAPI = {
    // Dynamically target Flask backend if served cross-origin (e.g. file:// or Live Server)
    BASE_URL: window.location.port === "5000" ? "" : "http://127.0.0.1:5000",

    /**
     * Fetches the complete list of available movie titles for autocomplete.
     * @returns {Promise<string[]>}
     */
    async getMoviesList() {
        try {
            const response = await fetch(`${this.BASE_URL}/api/movies`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Error fetching autocomplete movies list:", error);
            throw error;
        }
    },

    /**
     * Sends the selected movie query to compute recommendations.
     * @param {string} movieTitle 
     * @returns {Promise<Object[]>} Recommended movies with detailed metadata.
     */
    async getRecommendations(movieTitle) {
        try {
            const response = await fetch(`${this.BASE_URL}/api/recommend`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ movie: movieTitle })
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error calculating recommendations for '${movieTitle}':`, error);
            throw error;
        }
    },

    /**
     * Fetches aggregated analytics stats to populate Chart.js charts.
     * @returns {Promise<Object>} Aggregated analytics data payload.
     */
    async getAnalyticsData() {
        try {
            const response = await fetch(`${this.BASE_URL}/api/analytics`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Error fetching database analytics metrics:", error);
            throw error;
        }
    }
};
