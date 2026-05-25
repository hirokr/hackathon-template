import arcjet, { shield, detectBot, slidingWindow } from '@arcjet/node';

const ajKey = process.env.ARCJET_KEY as string | undefined;

if (!ajKey) {
  throw new Error('ARCJET_KEY environment variable is required');
}

const aj = arcjet({
  key: ajKey,
  rules: [
    shield({ mode: 'LIVE' }),
    detectBot({
      mode: 'LIVE',
      allow: ['CATEGORY:SEARCH_ENGINE', 'CATEGORY:PREVIEW'],
    }),
    slidingWindow({
      mode: 'LIVE',
      interval: '2s',
      max: 5,
    }),
  ],
});

export default aj;
