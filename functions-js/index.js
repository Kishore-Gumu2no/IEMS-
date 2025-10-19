const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp();

const db = admin.firestore();
const CREDITS_PER_REPORT = 10;

/**
 * A Cloud Function that triggers whenever a new document is created in the 'reports' collection.
 * It finds the user who created the report and adds credits to their profile.
 */
exports.awardCreditsForNewReport = functions.firestore
    .document("reports/{reportId}")
    .onCreate(async (snap, context) => {
      const reportData = snap.data();
      const userId = reportData.userId;

      if (!userId) {
        console.log("Report is missing a userId. No credits will be awarded.");
        return null;
      }

      // Get a reference to the user's document in the 'users' collection.
      const userRef = db.collection("users").doc(userId);

      try {
        // Use a transaction to safely update the user's score.
        await db.runTransaction(async (transaction) => {
          const userDoc = await transaction.get(userRef);

          if (!userDoc.exists) {
            // If the user document doesn't exist, create it with starting credits.
            console.log(`User document for ${userId} not found. Creating new one.`);
            transaction.set(userRef, {
              credits: CREDITS_PER_REPORT,
              userDisplayName: reportData.userDisplayName || "Anonymous",
            });
          } else {
            // If the user document exists, increment their credits.
            const newCredits = (userDoc.data().credits || 0) + CREDITS_PER_REPORT;
            console.log(`Updating credits for user ${userId} to ${newCredits}.`);
            transaction.update(userRef, { credits: newCredits });
          }
        });
        console.log("Transaction successfully committed!");
      } catch (e) {
        console.error("Transaction failed: ", e);
      }
      return null;
    });