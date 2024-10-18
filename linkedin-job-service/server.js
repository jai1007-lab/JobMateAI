const express = require('express');
const linkedIn = require('linkedin-jobs-api');

const app = express();
const port = 3000;

const axios = require('axios');

async function fetchJobsWithRetry(queryOptions, retries = 3, delay = 3000) {
    try {
        const response = await axios.get('https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search', { params: queryOptions });
        return response.data;
    } catch (error) {
        if (error.response && error.response.status === 429 && retries > 0) {
            console.log(`Rate limited. Retrying in ${delay / 1000} seconds...`);
            await new Promise(resolve => setTimeout(resolve, delay));
            return fetchJobsWithRetry(queryOptions, retries - 1, delay);
        } else {
            throw error;
        }
    }
}

app.get('/jobs', async (req, res) => {
    const queryOptions = {
        keyword: req.query.keyword,
        location: req.query.location,
        dateSincePosted: req.query.dateSincePosted || 'past Week',
        jobType: req.query.jobType || 'full time',
        remoteFilter: req.query.remoteFilter || 'remote',
        salary: req.query.salary,
        experienceLevel: req.query.experienceLevel || 'entry level',
        limit: req.query.limit || '10'
    };

    try {
        const jobs = await linkedIn.query(queryOptions);
        res.json(jobs);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch jobs' });
    }
});

app.listen(port, () => {
    console.log(`LinkedIn Job Service listening at http://localhost:${port}`);
});
