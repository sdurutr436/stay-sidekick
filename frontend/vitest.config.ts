import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'istanbul',
      include: ['src/**/*.ts'],
      exclude: [
        'src/environments/**',
        'src/main.ts',
        'src/app/app.config.ts',
        '**/*.spec.ts',
        '**/*.d.ts',
      ],
      thresholds: {
        statements: 90,
        branches: 90,
        functions: 90,
        lines: 90,
      },
      reporter: ['text', 'html', 'lcov'],
    },
  },
});
