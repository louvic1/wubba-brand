import type { CSSProperties } from 'react';

export const theme = {
  "colors": {
    "primary": "#0e0f12",
    "secondary": "#f1f0ec",
    "accent": "#ff2a36",
    "neutral-50": "#fbfaf6",
    "neutral-100": "#f1f0ec",
    "neutral-150": "#e7e6e2",
    "neutral-200": "#dad9d6",
    "neutral-300": "#bebebb",
    "neutral-400": "#989897",
    "neutral-500": "#787979",
    "neutral-600": "#5c5c5d",
    "neutral-700": "#434445",
    "neutral-800": "#2d2e30",
    "neutral-850": "#222325",
    "neutral-900": "#18191c",
    "neutral-950": "#0e0f12",
    "success": "#3aba6a",
    "warning": "#f2b036",
    "error": "#d4101e",
    "info": "#468de5"
  },
  "fonts": {
    "heading": "'Archivo', sans-serif",
    "body": "'Instrument Sans', sans-serif",
    "mono": "'Martian Mono', monospace"
  },
  "fontSizes": {
    "label": "12px",
    "small": "14px",
    "body": "16px",
    "lead": "21px",
    "h4": "21px",
    "h3": "28px",
    "h2": "38px",
    "h1": "50px",
    "display": "67px",
    "hero": "90px"
  },
  "lineHeights": {
    "label": "1.3",
    "small": "1.45",
    "body": "1.55",
    "lead": "1.45",
    "h4": "1.15",
    "h3": "1.1",
    "h2": "1.05",
    "h1": "1.02",
    "display": "1.0",
    "hero": "0.96"
  },
  "space": {
    "0": "0px",
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px",
    "5": "24px",
    "6": "32px",
    "7": "48px",
    "8": "64px",
    "9": "96px",
    "10": "128px"
  },
  "shadows": {
    "none": "none"
  },
  "radii": {
    "none": "0px",
    "sm": "4px",
    "md": "8px",
    "lg": "14px",
    "tile": "22%",
    "full": "9999px"
  },
  "borderWidths": {
    "thin": "1px",
    "medium": "2px",
    "thick": "4px"
  },
  "motion": {
    "durations": {
      "fast": "120ms",
      "normal": "200ms",
      "slow": "320ms"
    },
    "easings": {
      "ease-out": "cubic-bezier(0.2, 0, 0, 1)",
      "ease-in-out": "cubic-bezier(0.6, 0, 0.2, 1)"
    },
    "transitions": {
      "fade": "opacity 200ms cubic-bezier(0, 0, 0.15, 1)",
      "slide": "transform 200ms cubic-bezier(0, 0, 0.15, 1)",
      "scale": "transform 100ms cubic-bezier(0, 0, 0.15, 1)",
      "color": "color 300ms cubic-bezier(0, 0, 0.15, 1), background-color 300ms cubic-bezier(0, 0, 0.15, 1)",
      "all": "all 200ms cubic-bezier(0, 0, 0.15, 1)"
    }
  },
  "gradients": {}
} as const;

export type Theme = typeof theme;
