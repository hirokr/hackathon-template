import { Strategy as GoogleStrategy } from 'passport-google-oauth2';
import passport from 'passport';
import { CreateGoogleUser } from '#src/services/google.service.ts';
import { findUserById } from '#src/services/user.service.ts';
import { getOptionalEnv, getRequiredEnv } from '#src/utils/env.ts';

const GOOGLE_CLIENT_ID = getRequiredEnv('GOOGLE_CLIENT_ID');
const GOOGLE_CLIENT_SECRET = getRequiredEnv('GOOGLE_CLIENT_SECRET');
const GOOGLE_CALLBACK_URL =
  getOptionalEnv(
    'GOOGLE_CALLBACK_URL',
    'http://localhost:8000/api/auth/google/callback'
  ) || 'http://localhost:8000/api/auth/google/callback';

passport.use(
  new GoogleStrategy(
    {
      clientID: GOOGLE_CLIENT_ID,
      clientSecret: GOOGLE_CLIENT_SECRET,
      callbackURL: GOOGLE_CALLBACK_URL,
      passReqToCallback: true,
    },
    async (
      request: any,
      accessToken: any,
      refreshToken: any,
      profile: any,
      done: any
    ) => {
      try {
        const user = await CreateGoogleUser(profile);
        return done(null, user);
      } catch (err) {
        return done(err, null);
      }
    }
  )
);

passport.serializeUser((user: any, done) => {
  done(null, user.id);
});

passport.deserializeUser(async (id: string, done) => {
  try {
    const user = await findUserById(id);
    done(null, user);
  } catch (err) {
    done(err, null);
  }
});
