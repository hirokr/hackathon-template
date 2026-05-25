/** @type {import('jest').Config} */
const config = {
  clearMocks: true,

  collectCoverage: true,

  coverageDirectory: 'coverage',

  testEnvironment: 'node',

  extensionsToTreatAsEsm: ['.ts'],

  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        useESM: true,
        tsconfig: 'tsconfig.json',
      },
    ],
  },

  moduleNameMapper: {
    '^#src/(.*)$': '<rootDir>/src/$1',
    '^#config/(.*)$': '<rootDir>/src/config/$1',
    '^#controllers/(.*)$': '<rootDir>/src/controllers/$1',
    '^#models/(.*)$': '<rootDir>/src/models/$1',
    '^#routes/(.*)$': '<rootDir>/src/routes/$1',
    '^#services/(.*)$': '<rootDir>/src/services/$1',
    '^#middlewares/(.*)$': '<rootDir>/src/middlewares/$1',
    '^#utils/(.*)$': '<rootDir>/src/utils/$1',
    '^#validations/(.*)$': '<rootDir>/src/validations/$1',
    '^(\\.{1,2}/.*)\\.js$': '$1',
  },

};

export default config;
