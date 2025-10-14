// ------------------------
// Required Libraries
// ------------------------
const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const cors = require("cors");
const axios = require("axios"); // <-- FINAL ADDITION: Import axios

// ------------------------
// Firebase Initialization
// ------------------------
admin.initializeApp();
const db = admin.firestore();

// ------------------------
// Express App Setup
// ------------------------
const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

// ------------------------
// Constants / Config
// ------------------------
// IMPORTANT: Replace this with your actual ML model endpoint
const ML_MODEL_API_ENDPOINT = "https://your-ml-model-endpoint.com/predict";

// ------------------------
// 1️⃣ Submit Report (Callable Function)
// ------------------------
exports.submitReport = functions.https.onCall(async (data, context) => {
    // Authentication Check
    if (!context.auth) {
        throw new functions.https.HttpsError('unauthenticated','User must be authenticated to submit reports.');
    }

    const { description, imageUrl, location } = data;

    // --- ROBUSTNESS: INPUT VALIDATION ---
    if (!description || typeof description !== 'string' || description.trim() === '') {
        throw new functions.https.HttpsError('invalid-argument', 'The report must include a valid, non-empty description.');
    }
    if (!imageUrl || typeof imageUrl !== 'string') {
        throw new functions.https.HttpsError('invalid-argument', 'The report must include a valid imageUrl.');
    }
    if (!location) {
        throw new functions.https.HttpsError('invalid-argument', 'The report must include a location.');
    }
    // --- END VALIDATION ---

    const userId = context.auth.uid;
    const newReport = { userId, description, imageUrl, location, timestamp: admin.firestore.FieldValue.serverTimestamp() };

    const reportRef = await db.collection("reports").add(newReport);
    return { success: true, reportId: reportRef.id };
});

// ------------------------
// 2️⃣ Express API (includes /reportIssue and /processAIResult)
// ------------------------
app.post("/reportIssue", async (req, res) => {
    const { userId, description, imageUrl, location } = req.body;
    // --- ROBUSTNESS: INPUT VALIDATION ---
    if (!userId || typeof userId !== 'string') {
        return res.status(400).send({ success: false, error: 'A valid userId must be provided.' });
    }
    if (!description || typeof description !== 'string' || description.trim() === '') {
        return res.status(400).send({ success: false, error: 'A valid, non-empty description must be provided.' });
    }
    // --- END VALIDATION ---
    try {
        const reportRef = await db.collection("reports").add({ userId, description, imageUrl, location, timestamp: admin.firestore.FieldValue.serverTimestamp() });
        res.status(200).send({ success: true, reportId: reportRef.id });
    } catch (error) {
        console.error("Error in /reportIssue:", error);
        res.status(500).send({ success: false, error: "Internal Server Error" });
    }
});

// --- FINAL 5%: EXTERNAL INTEGRATION ---
app.post("/processAIResult", async (req, res) => {
    const { reportId } = req.body;
    // --- ROBUSTNESS: INPUT VALIDATION ---
    if (!reportId || typeof reportId !== 'string') {
        return res.status(400).send({ success: false, error: 'A valid reportId must be provided.' });
    }
    // --- END VALIDATION ---

    try {
        // 1. Fetch the report data from Firestore
        const reportRef = db.collection("reports").doc(reportId);
        const reportSnap = await reportRef.get();

        if (!reportSnap.exists) {
            return res.status(404).send({ success: false, error: 'Report not found.' });
        }
        const reportData = reportSnap.data();

        // 2. Call the external ML model API with the report data
        const mlResponse = await axios.post(ML_MODEL_API_ENDPOINT, {
            description: reportData.description,
            imageUrl: reportData.imageUrl,
        });

        // 3. Extract the analysis and update the report in Firestore
        const analysisResult = mlResponse.data; // Assuming the ML API returns the result directly
        await reportRef.update({ analysisResult });

        res.status(200).send({ success: true, result: analysisResult });

    } catch (error) {
        // This catch block now handles Firestore errors AND network errors from axios
        console.error(`Error processing AI result for report ${reportId}:`, error);
        res.status(500).send({ success: false, error: "Failed to process AI result." });
    }
});
// We export the entire Express app as a single API function
exports.api = functions.https.onRequest(app);

// ------------------------
// 4️⃣ Dashboard Data (Callable Function)
// ------------------------
exports.getDashboardData = functions.https.onCall(async (data, context) => {
    if (!context.auth) {
        throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated.');
    }
    const reportsSnap = await db.collection("reports").orderBy("timestamp", "desc").limit(50).get();
    const usersSnap = await db.collection("users").orderBy("points", "desc").limit(10).get();
    const reports = reportsSnap.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    const leaderboard = usersSnap.docs.map(doc => ({ uid: doc.id, ...doc.data() }));
    return { reports, leaderboard };
});

// ------------------------
// 5️⃣ Gamification Trigger: Points & Badges
// ------------------------
exports.onReportCreated = functions.firestore.document('reports/{reportId}')
    .onCreate(async (snap, context) => {
        const reportData = snap.data();
        const userId = reportData.userId;
        if (!userId) { return null; }

        const userRef = db.collection('users').doc(userId);
        try {
            await userRef.set({ points: admin.firestore.FieldValue.increment(10) }, { merge: true });
            const userSnap = await userRef.get();
            const userData = userSnap.data();
            if (!userData) { return null; }

            const points = userData.points || 0;
            const badges = userData.badges || [];
            const badgeThresholds = [
                { points: 50, badge: 'Rookie Reporter' },
                { points: 200, badge: 'City Hero' },
                { points: 500, badge: 'Master Citizen' },
            ];
            const badgesToAward = badgeThresholds
                .filter(b => points >= b.points && !badges.includes(b.badge))
                .map(b => b.badge);
            if (badgesToAward.length > 0) {
                await userRef.update({ badges: admin.firestore.FieldValue.arrayUnion(...badgesToAward) });
            }
        } catch (error) {
            console.error(`Error updating points/badges for user ${userId}:`, error);
        }
        return null;
    });

