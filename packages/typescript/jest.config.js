import { createDefaultEsmPreset } from "ts-jest";

const tsJestDefaultEsmPreset = createDefaultEsmPreset();

export default {
  testEnvironment: "node",
  testPathIgnorePatterns: ["<rootDir>/dist/", "<rootDir>/node_modules/"],
  ...tsJestDefaultEsmPreset,
};
