/** Charge .env et expose l'URL API à l'app (Expo Go + build) */
const appJson = require('./app.json');

// IP locale du PC — même valeur que mobile/.env
const API_URL =
  process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.102:8000';

module.exports = {
  expo: {
    ...appJson.expo,
    extra: {
      apiUrl: API_URL,
    },
  },
};
